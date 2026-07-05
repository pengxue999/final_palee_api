import atexit
import os
import queue
import subprocess
import sys
import threading

from playwright.sync_api import sync_playwright

from app.services.pdf.assets import BROWSER_DIR, PROJECT_ROOT


os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(BROWSER_DIR))


def _find_browser_binary() -> str | None:
    patterns = (
        "chromium-*/chrome-win/chrome.exe",
        "chromium-*/chrome-linux/chrome",
        "chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
        "chromium_headless_shell-*/chrome-win/headless_shell.exe",
        "chromium_headless_shell-*/chrome-linux/headless_shell",
        "chromium_headless_shell-*/chrome-mac/headless_shell",
    )

    configured_path = PROJECT_ROOT / ".playwright-browsers"
    for browser_root in (configured_path, BROWSER_DIR):
        if not browser_root.exists():
            continue

        for pattern in patterns:
            matches = sorted(browser_root.glob(pattern), reverse=True)
            if matches:
                return str(matches[0])

    return None


def resolve_chromium_executable() -> str | None:
    chromium_executable = _find_browser_binary()
    if chromium_executable is not None:
        return chromium_executable

    BROWSER_DIR.mkdir(parents=True, exist_ok=True)
    install_env = os.environ.copy()
    install_env["PLAYWRIGHT_BROWSERS_PATH"] = str(BROWSER_DIR)
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=True,
        env=install_env,
    )

    return _find_browser_binary()


# --- Single dedicated render thread owning one Chromium --------------------
#
# Launching/closing Chromium per request was the bottleneck (~1-3s each).
# Playwright's sync API binds its objects to the thread that created them,
# and FastAPI runs sync endpoints across a threadpool — so we cannot touch a
# shared browser from arbitrary threads. Instead, ONE dedicated worker thread
# owns Playwright + a single long-lived browser; every request hands its job
# to that thread via a queue and waits for the result. One launch total
# (warmed at startup), and each render only opens/closes a cheap page (~250ms).


class _RenderJob:
    __slots__ = ("kwargs", "html", "event", "result", "error")

    def __init__(self, html: str, kwargs: dict) -> None:
        self.html = html
        self.kwargs = kwargs
        self.event = threading.Event()
        self.result: bytes | None = None
        self.error: BaseException | None = None


class _RenderWorker:
    def __init__(self) -> None:
        self._queue: "queue.Queue[_RenderJob | None]" = queue.Queue()
        self._thread = threading.Thread(
            target=self._run, name="pdf-render-worker", daemon=True
        )
        self._started = False
        self._lock = threading.Lock()

    def _ensure_started(self) -> None:
        if self._started:
            return
        with self._lock:
            if not self._started:
                self._thread.start()
                self._started = True

    def _run(self) -> None:
        chromium_executable = resolve_chromium_executable()
        with sync_playwright() as playwright:
            launch_kwargs = {
                "headless": True,
                "args": ["--font-render-hinting=medium"],
            }
            if chromium_executable is not None:
                launch_kwargs["executable_path"] = chromium_executable
            browser = playwright.chromium.launch(**launch_kwargs)
            try:
                while True:
                    job = self._queue.get()
                    if job is None:
                        break
                    try:
                        job.result = self._render(browser, job.html, job.kwargs)
                    except BaseException as exc:  # noqa: BLE001
                        job.error = exc
                    finally:
                        job.event.set()
            finally:
                browser.close()

    @staticmethod
    def _render(browser, html: str, kwargs: dict) -> bytes:
        page = browser.new_page(
            viewport={
                "width": kwargs["viewport_width"],
                "height": kwargs["viewport_height"],
            },
            locale="lo-LA",
        )
        try:
            page.set_content(html, wait_until="load")
            page.emulate_media(media="screen")
            pdf_options = {
                "format": "A4",
                "landscape": kwargs["viewport_width"] > kwargs["viewport_height"],
                "print_background": True,
                "margin": {
                    "top": kwargs["margin_top"],
                    "right": kwargs["margin_right"],
                    "bottom": kwargs["margin_bottom"],
                    "left": kwargs["margin_left"],
                },
                "prefer_css_page_size": True,
            }
            header_template = kwargs.get("header_template")
            footer_template = kwargs.get("footer_template")
            if header_template is not None or footer_template is not None:
                pdf_options["display_header_footer"] = True
                pdf_options["header_template"] = header_template or "<div></div>"
                pdf_options["footer_template"] = footer_template or "<div></div>"
            return page.pdf(**pdf_options)
        finally:
            page.close()

    def submit(self, html: str, kwargs: dict) -> bytes:
        self._ensure_started()
        job = _RenderJob(html, kwargs)
        self._queue.put(job)
        job.event.wait()
        if job.error is not None:
            raise job.error
        assert job.result is not None
        return job.result

    def shutdown(self) -> None:
        if self._started:
            self._queue.put(None)
            self._thread.join(timeout=10)


_worker = _RenderWorker()


def warmup_engine() -> None:
    """Launch the browser now so the first real request is already fast."""
    _worker.submit(
        "<!doctype html><html><body></body></html>",
        {
            "viewport_width": 100,
            "viewport_height": 100,
            "margin_top": "0mm",
            "margin_right": "0mm",
            "margin_bottom": "0mm",
            "margin_left": "0mm",
        },
    )


def shutdown_engines() -> None:
    """Stop the render worker and close its browser. Call on app shutdown."""
    _worker.shutdown()


atexit.register(shutdown_engines)


def render_pdf_document(
    html: str,
    *,
    viewport_width: int,
    viewport_height: int,
    margin_top: str = "0mm",
    margin_right: str = "0mm",
    margin_bottom: str = "0mm",
    margin_left: str = "0mm",
    header_template: str | None = None,
    footer_template: str | None = None,
) -> bytes:
    return _worker.submit(
        html,
        {
            "viewport_width": viewport_width,
            "viewport_height": viewport_height,
            "margin_top": margin_top,
            "margin_right": margin_right,
            "margin_bottom": margin_bottom,
            "margin_left": margin_left,
            "header_template": header_template,
            "footer_template": footer_template,
        },
    )

from base64 import b64encode
from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_DIR = PROJECT_ROOT / "app" / "templates"
BROWSER_DIR = PROJECT_ROOT / ".playwright-browsers"
FONT_DIR = PROJECT_ROOT / "assets" / "fonts"


def resolve_font_paths() -> tuple[Path, Path]:
    regular_font = FONT_DIR / "NotoSansLao-Regular.ttf"
    bold_font = FONT_DIR / "NotoSansLao-Bold.ttf"

    if regular_font.exists() and bold_font.exists():
        return regular_font, bold_font

    raise FileNotFoundError(
        f"NotoSansLao fonts not found in {FONT_DIR} for receipt PDF generation."
    )


@lru_cache(maxsize=1)
def font_data_urls() -> tuple[str, str]:
    regular_font, bold_font = resolve_font_paths()
    regular_bytes = b64encode(regular_font.read_bytes()).decode("ascii")
    bold_bytes = b64encode(bold_font.read_bytes()).decode("ascii")
    return (
        f"data:font/ttf;base64,{regular_bytes}",
        f"data:font/ttf;base64,{bold_bytes}",
    )


@lru_cache(maxsize=1)
def template_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(template_name: str, context: dict[str, object]) -> str:
    template = template_environment().get_template(template_name)
    return template.render(**context)
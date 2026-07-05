from datetime import datetime

from app.services.pdf.assets import font_data_urls


def build_registration_report_context(
    report_data: dict[str, object],
) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    filters = report_data.get("filters") or {}
    summary = report_data.get("summary") or {}

    filter_items: list[str] = []

    def add_filter(label: str, value: object) -> None:
        if value is None:
            return
        text = str(value).strip()
        if text:
            filter_items.append(f"{label}: {text}")

    add_filter("ສົກຮຽນ", filters.get("academic_year_name"))
    add_filter("ວິຊາ", filters.get("subject_name"))
    add_filter("ລະດັບ/ຊັ້ນຮຽນ", filters.get("level_name"))
    add_filter("ສະຖານະການຊຳລະ", filters.get("status_label"))

    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_count": report_data.get("total_count", 0),
        "summary": {
            "total": summary.get("total", 0),
            "paid": summary.get("paid", 0),
            "partial": summary.get("partial", 0),
            "unpaid": summary.get("unpaid", 0),
        },
        "registrations": report_data.get("registrations", []),
        "filter_items": filter_items,
    }

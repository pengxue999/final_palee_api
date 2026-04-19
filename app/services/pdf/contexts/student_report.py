from datetime import datetime

from app.services.pdf.assets import font_data_urls


def build_student_report_context(report_data: dict[str, object]) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    filters = report_data.get("filters") or {}

    filter_items: list[str] = []

    def add_filter(label: str, value: object) -> None:
        if value is None:
            return
        text = str(value).strip()
        if text:
            filter_items.append(f"{label}: {text}")

    add_filter("ສົກຮຽນ", filters.get("academic_year_name"))
    add_filter("ແຂວງ", filters.get("province_name"))
    add_filter("ເມືອງ", filters.get("district_name"))
    add_filter("ສະຖານະທຶນ", filters.get("scholarship"))
    add_filter("ເພດ", filters.get("gender"))

    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_count": report_data.get("total_count", 0),
        "students": report_data.get("students", []),
        "filter_items": filter_items,
    }
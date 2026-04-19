from datetime import datetime

from app.services.pdf.assets import font_data_urls


def build_popular_subject_level_report_context(
    report_data: dict[str, object],
) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    filters = report_data.get("filters") or {}
    summary = report_data.get("summary") or {}
    students = report_data.get("students") or []

    subject_name = filters.get("subject_name") or "-"
    level_name = filters.get("level_name") or "-"
    subject_category = filters.get("subject_category") or "-"
    academic_year_name = filters.get("academic_year_name") or "ທັງໝົດ"

    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "title": f"{subject_name} {level_name}",
        "subject_name": subject_name,
        "level_name": level_name,
        "subject_category": subject_category,
        "academic_year_name": academic_year_name,
        "total_students": summary.get("total_students") or 0,
        "students": students,
    }
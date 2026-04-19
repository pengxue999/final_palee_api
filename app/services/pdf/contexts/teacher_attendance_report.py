from datetime import datetime

from app.services.pdf.assets import font_data_urls
from app.services.pdf.formatters import format_month_label, format_plain_currency


def build_teacher_attendance_report_context(
    report_data: dict[str, object],
) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    filters = report_data.get("filters") or {}
    logs = report_data.get("logs") or []
    month_label = format_month_label(filters.get("month"))
    show_teacher_column = not bool(filters.get("teacher_id"))

    filter_items: list[str] = []

    def add_filter(label: str, value: object) -> None:
        if value is None:
            return
        text = str(value).strip()
        if text:
            filter_items.append(f"{label}: {text}")

    add_filter("ສົກຮຽນ", filters.get("academic_year_name"))
    add_filter("ເດືອນ", month_label)
    add_filter("ສະຖານະ", filters.get("status"))
    add_filter("ອາຈານ", filters.get("teacher_name"))

    present_count = sum(1 for log in logs if log.get("status") == "ຂຶ້ນສອນ")
    absent_count = sum(1 for log in logs if log.get("status") == "ຂາດສອນ")
    total_hours = sum(
        float(log.get("hourly") or 0)
        for log in logs
        if log.get("status") == "ຂຶ້ນສອນ"
    )
    total_amount = sum(
        float(log.get("total_amount") or 0)
        for log in logs
        if log.get("status") == "ຂຶ້ນສອນ"
    )

    prepared_logs = []
    for log in logs:
        base_remark = str(log.get("remark") or "").strip()
        substitute_note = ""
        if log.get("is_substitute"):
            substitute_teacher = " ".join(
                part
                for part in [
                    log.get("substitute_for_teacher_name"),
                    log.get("substitute_for_teacher_lastname"),
                ]
                if part
            ).strip()
            substitute_subject = (log.get("substitute_for_subject_name") or "").strip()
            substitute_parts: list[str] = []
            if substitute_teacher:
                substitute_parts.append(substitute_teacher)
            if substitute_subject:
                substitute_parts.append(f"ວິຊາ{substitute_subject}")
            if substitute_parts:
                substitute_detail = " - ".join(substitute_parts)
                substitute_note = f"ສອນແທນ({substitute_detail})"
            else:
                substitute_note = "ສອນແທນ"

        remark_parts = [base_remark]
        if substitute_note and "ສອນແທນ" not in base_remark:
            remark_parts.append(substitute_note)
        remark_display = " | ".join(part for part in remark_parts if part)

        prepared_logs.append(
            {
                **log,
                "subject_display": log.get("substitute_for_subject_name")
                or log.get("subject_name")
                or "-",
                "hourly_display": f"{float(log.get('hourly') or 0):.0f}",
                "hourly_rate_display": format_plain_currency(
                    float(log.get("hourly_rate") or 0)
                ),
                "total_amount_display": format_plain_currency(
                    float(log.get("total_amount") or 0)
                ),
                "remark_display": remark_display or "-",
            }
        )

    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_count": report_data.get("total_count", 0),
        "present_count": present_count,
        "absent_count": absent_count,
        "total_hours": f"{total_hours:,.0f} ຊ.ມ",
        "total_amount": format_plain_currency(total_amount),
        "logs": prepared_logs,
        "filter_items": filter_items,
        "show_teacher_column": show_teacher_column,
    }
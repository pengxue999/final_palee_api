from datetime import datetime

from app.services.pdf.assets import font_data_urls
from app.services.pdf.formatters import format_plain_currency, format_report_date_text


def build_salary_payment_report_context(
    report_data: dict[str, object],
) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    filters = report_data.get("filters") or {}
    summary = report_data.get("summary") or {}
    payments = report_data.get("payments") or []

    filter_items: list[str] = []

    def add_filter(label: str, value: object) -> None:
        if value is None:
            return
        text = str(value).strip()
        if text:
            filter_items.append(f"{label}: {text}")

    add_filter("ເດືອນ", filters.get("month_name"))
    add_filter("ອາຈານ", filters.get("teacher_name"))
    add_filter("ສະຖານະ", filters.get("status"))

    prepared_payments = []
    for payment in payments:
        month_name = payment.get("month_name") or "-"
        year_text = str(payment.get("year") or "-")
        prepared_payments.append(
            {
                **payment,
                "period_display": f"{month_name} {year_text}",
                "payment_date_display": format_report_date_text(
                    payment.get("payment_date")
                ),
                "amount_display": format_plain_currency(
                    float(payment.get("total_amount") or 0)
                ),
            }
        )

    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_count": report_data.get("total_count", 0),
        "total_amount": format_plain_currency(float(summary.get("total_amount") or 0)),
        "paid_count": summary.get("paid_count", 0),
        "pending_count": summary.get("pending_count", 0),
        "unique_teacher_count": summary.get("unique_teacher_count", 0),
        "filter_items": filter_items,
        "payments": prepared_payments,
    }
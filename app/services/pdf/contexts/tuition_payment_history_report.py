from datetime import datetime

from app.schemas.tuition_payment import TuitionPaymentHistoryReportRequest
from app.services.pdf.assets import font_data_urls
from app.services.pdf.formatters import format_currency, format_date


def build_tuition_payment_history_report_context(
    data: TuitionPaymentHistoryReportRequest,
) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "generated_at": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "registration_id": data.registration_id,
        "student_id": data.student_id or "-",
        "student_name": data.student_name,
        "registration_date": format_date(data.registration_date),
        "total_fee": format_currency(data.total_fee),
        "total_paid_amount": format_currency(data.total_paid_amount),
        "remaining_amount": format_currency(data.remaining_amount),
        "installment_count": data.installment_count,
        "payment_items": [
            {
                "installment_index": item.installment_index,
                "invoice_id": item.invoice_id,
                "pay_date": format_date(item.pay_date),
                "payment_method": item.payment_method,
                "paid_amount": format_currency(item.paid_amount),
                "cumulative_paid_amount": format_currency(item.cumulative_paid_amount),
                "remaining_amount": format_currency(item.remaining_amount),
                "status": item.status,
            }
            for item in data.payment_items
        ],
    }
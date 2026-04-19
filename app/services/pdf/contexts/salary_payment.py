from app.schemas.salary_payment import SalaryPaymentReceiptRequest
from app.services.pdf.assets import font_data_urls
from app.services.pdf.formatters import format_currency, format_date, format_hours


def build_salary_payment_context(
    data: SalaryPaymentReceiptRequest,
) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    is_fully_paid = data.remaining_amount <= 0
    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "salary_payment_id": data.salary_payment_id,
        "invoice_id": data.invoice_id,
        "teacher_id": data.teacher_id,
        "teacher_name": data.teacher_name,
        "user_name": data.user_name,
        "pay_date": format_date(data.pay_date),
        "payment_period": f"{data.month_label} {data.year}",
        "installment_label": str(data.installment_index),
        "installment_total": str(data.installment_total),
        "total_hours": format_hours(data.total_hours),
        "hourly_rate": format_currency(data.hourly_rate),
        "expected_amount": format_currency(data.expected_amount),
        "prior_debt": format_currency(abs(data.prior_debt)),
        "prior_debt_label": "ຍອດຄ້າງຈາກເດືອນກ່ອນ"
        if data.prior_debt >= 0
        else "ຍອດເກີນຈ່າຍຈາກເດືອນກ່ອນ",
        "has_prior_debt": data.prior_debt != 0,
        "outstanding_before_payment": format_currency(data.outstanding_before_payment),
        "paid_amount": format_currency(data.paid_amount),
        "cumulative_paid_amount": format_currency(data.cumulative_paid_amount),
        "remaining_amount": format_currency(data.remaining_amount),
        "status": data.status,
        "watermark_label": "ຈ່າຍແລ້ວ" if is_fully_paid else "ຈ່າຍບາງສ່ວນ",
        "watermark_class": "is-paid" if is_fully_paid else "is-partial",
    }
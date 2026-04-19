from app.schemas.registration import RegistrationReceiptRequest
from app.services.pdf.assets import font_data_urls
from app.services.pdf.formatters import format_currency, format_date


def build_registration_context(data: RegistrationReceiptRequest) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "registration_id": data.registration_id,
        "registration_date": format_date(data.registration_date),
        "student_name": data.student_name,
        "selected_fees": [
            {
                "subject_name": item.subject_name,
                "level_name": item.level_name,
                "fee": format_currency(item.fee),
            }
            for item in data.selected_fees
        ],
        "tuition_fee": format_currency(data.tuition_fee),
        "total_fee": format_currency(data.total_fee),
        "discount_amount": format_currency(data.discount_amount),
        "net_fee": format_currency(data.net_fee),
        "has_discount": data.discount_amount > 0,
    }
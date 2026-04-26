from datetime import date
from decimal import Decimal

from app.models.donation import Donation
from app.services.pdf.assets import font_data_urls, image_data_url
from app.services.pdf.formatters import format_date
from app.utils.donation_category import is_cash_donation_name


def _format_amount(value: Decimal, unit_name: str | None) -> str:
    amount_text = f"{int(value):,}"
    unit_text = (unit_name or "").strip()
    return f"{amount_text} {unit_text}".strip()


def build_donation_certificate_context(donation: Donation) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    donor_name = "ຜູ້ບໍລິຈາກ"
    is_cash_donation = is_cash_donation_name(donation.donation_category)

    if donation.donor is not None:
        donor_name = (
            f"{donation.donor.donor_name} {donation.donor.donor_lastname}".strip()
            or donor_name
        )

    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "logo_url": image_data_url("logo.png"),
        "certificate_title": "ໃບກຽດຕິຄຸນ",
        "organization_name": "ສູນປາລີ ບຳລຸງນັກຮຽນເກັ່ງ",
        "organization_caption": "ຜູ້ອຳນວຍການ ສູນປາລີ ບຳລຸງນັກຮຽນເກັ່ງ",
        "donor_name": donor_name,
        "donor_section": (donation.donor.section if donation.donor else None) or "",
        "donation_name": donation.donation_name,
        "donation_category": donation.donation_category,
        "donation_amount_label": "ລວມມູນຄ່າ" if is_cash_donation else "ຈຳນວນ",
        "amount_text": _format_amount(
            donation.amount,
            donation.unit.unit_name if donation.unit else None,
        ),
        "certificate_number": "",
        "issue_date": format_date(date.today()),
        "donation_date": format_date(donation.donation_date),
        "description": (donation.description or "").strip(),
        "donation_id": donation.donation_id,
    }
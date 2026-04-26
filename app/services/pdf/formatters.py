from datetime import date, datetime
from decimal import Decimal


def format_currency(value: Decimal) -> str:
    return f"{int(value):,} ກີບ"


def format_date(value: date | datetime) -> str:
    if isinstance(value, datetime):
        has_time = value.hour != 0 or value.minute != 0 or value.second != 0
        return value.strftime("%d-%m-%Y %H:%M:%S" if has_time else "%d/%m/%Y")

    return value.strftime("%d/%m/%Y")


def format_hours(value: float) -> str:
    if float(value).is_integer():
        return f"{int(value):,} ຊົ່ວໂມງ"
    return f"{value:,.1f} ຊົ່ວໂມງ"


def format_plain_currency(value: float | int | Decimal) -> str:
    return f"{int(value):,} ກີບ"


def format_finance_currency(value: float | int | Decimal) -> str:
    return f"{int(value):,} ₭"


def format_report_date_text(value: object) -> str:
    if value is None:
        return "-"

    text = str(value).strip()
    if not text:
        return "-"

    try:
        return datetime.fromisoformat(text).strftime("%d-%m-%Y")
    except ValueError:
        return text


def format_month_label(month_value: object) -> str | None:
    if month_value is None:
        return None

    text = str(month_value).strip()
    if not text:
        return None

    month_names = {
        1: "ມັງກອນ",
        2: "ກຸມພາ",
        3: "ມີນາ",
        4: "ເມສາ",
        5: "ພຶດສະພາ",
        6: "ມິຖຸນາ",
        7: "ກໍລະກົດ",
        8: "ສິງຫາ",
        9: "ກັນຍາ",
        10: "ຕຸລາ",
        11: "ພະຈິກ",
        12: "ທັນວາ",
    }

    try:
        _, month_part = text.split("-", 1)
        month_number = int(month_part)
    except (ValueError, AttributeError):
        return text

    return month_names.get(month_number, text)
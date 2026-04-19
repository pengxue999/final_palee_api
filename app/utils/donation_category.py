CASH_DONATION_CATEGORY = "ເງິນສົດ"
IN_KIND_DONATION_CATEGORY = "ວັດຖຸ"
FIXED_DONATION_CATEGORIES = (
    CASH_DONATION_CATEGORY,
    IN_KIND_DONATION_CATEGORY,
)


def normalize_donation_category_name(name: str | None) -> str:
    normalized_name = (name or "").strip()
    if normalized_name == CASH_DONATION_CATEGORY:
        return CASH_DONATION_CATEGORY
    return IN_KIND_DONATION_CATEGORY


def is_cash_donation_name(name: str | None) -> bool:
    return normalize_donation_category_name(name) == CASH_DONATION_CATEGORY

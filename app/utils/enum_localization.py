from __future__ import annotations


_REGISTRATION_STATUS_LABELS = {
    "PAID": "ຈ່າຍແລ້ວ",
    "UNPAID": "ຍັງບໍ່ທັນຈ່າຍ",
    "PARTIAL": "ຈ່າຍບາງສ່ວນ",
}

_GENDER_LABELS = {
    "MALE": "ຊາຍ",
    "FEMALE": "ຍິງ",
}

_SCHOLARSHIP_LABELS = {
    "SCHOLARSHIP": "ໄດ້ຮັບທຶນ",
    "NO_SCHOLARSHIP": "ບໍ່ໄດ້ຮັບທຶນ",
}

_PAYMENT_METHOD_LABELS = {
    "CASH": "ເງິນສົດ",
    "TRANSFER": "ເງິນໂອນ",
}

_TEACHING_STATUS_LABELS = {
    "TEACHING": "ຂຶ້ນສອນ",
    "ABSENT": "ຂາດສອນ",
}


def _normalize_enum_value(value: str | None) -> str:
    if value is None:
        return ""
    normalized = str(value).strip()
    if "." in normalized:
        normalized = normalized.split(".")[-1].strip()
    return normalized


def localize_registration_status(value: str | None) -> str:
    normalized = _normalize_enum_value(value)
    return _REGISTRATION_STATUS_LABELS.get(normalized, normalized)


def localize_payment_method(value: str | None) -> str:
    normalized = _normalize_enum_value(value)
    return _PAYMENT_METHOD_LABELS.get(normalized, normalized)


def localize_gender(value: str | None) -> str:
    normalized = _normalize_enum_value(value)
    return _GENDER_LABELS.get(normalized, normalized)


def api_gender(value: str | None) -> str:
    normalized = _normalize_enum_value(value)
    for key, label in _GENDER_LABELS.items():
        if normalized in {key, label}:
            return key
    return normalized


def localize_scholarship(value: str | None) -> str:
    normalized = _normalize_enum_value(value)
    return _SCHOLARSHIP_LABELS.get(normalized, normalized)


def api_scholarship(value: str | None) -> str:
    normalized = _normalize_enum_value(value)
    for key, label in _SCHOLARSHIP_LABELS.items():
        if normalized in {key, label}:
            return key
    return normalized


def localize_teaching_status(value: str | None) -> str:
    normalized = _normalize_enum_value(value)
    return _TEACHING_STATUS_LABELS.get(normalized, normalized)


def api_teaching_status(value: str | None) -> str:
    normalized = _normalize_enum_value(value)
    for key, label in _TEACHING_STATUS_LABELS.items():
        if normalized in {key, label}:
            return key
    return normalized


def is_paid_status(value: str | None) -> bool:
    return _normalize_enum_value(value).upper() == "PAID"


def is_pending_salary_status(value: str | None) -> bool:
    normalized = _normalize_enum_value(value)
    if not normalized:
        return False
    upper_value = normalized.upper()
    return upper_value in {"PARTIAL", "UNPAID", "PENDING"} or normalized in {
        "ຄ້າງຈ່າຍ",
        "ຈ່າຍບາງສ່ວນ",
        "ຍັງບໍ່ທັນຈ່າຍ",
    }

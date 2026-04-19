from enum import Enum


class RegistrationStatusEnum(str, Enum):
    PAID = "ຈ່າຍແລ້ວ"
    UNPAID = "ຍັງບໍ່ທັນຈ່າຍ"
    PARTIAL = "ຈ່າຍບາງສ່ວນ"

from enum import Enum


class RegistrationStatusEnum(str, Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    PARTIAL = "PARTIAL"

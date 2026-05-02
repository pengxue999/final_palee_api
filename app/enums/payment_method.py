from enum import Enum


class PaymentMethodEnum(str, Enum):
    CASH = "CASH"
    TRANSFER = "TRANSFER"

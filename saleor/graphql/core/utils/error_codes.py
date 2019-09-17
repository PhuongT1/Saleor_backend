from enum import Enum

from ....account.error_codes import AccountErrorCode
from ....checkout.error_codes import CheckoutErrorCode
from ....core.error_codes import ShopErrorCode
from ....extensions.error_codes import ExtensionsErrorCode
from ....giftcard.error_codes import GiftCardErrorCode
from ....menu.error_codes import MenuErrorCode
from ....order.error_codes import OrderErrorCode
from ....payment.error_codes import PaymentErrorCode
from ....product.error_codes import ProductErrorCode
from ....shipping.error_codes import ShippingErrorCode

DJANGO_VALIDATORS_ERROR_CODES = [
    "invalid",
    "invalid_extension",
    "limit_value",
    "max_decimal_places",
    "max_digits",
    "max_length",
    "max_value",
    "max_whole_digits",
    "min_length",
    "min_value",
    "null_characters_not_allowed",
]

DJANGO_FORM_FIELDS_ERROR_CODES = [
    "contradiction",
    "empty",
    "incomplete",
    "invalid_choice",
    "invalid_date",
    "invalid_image",
    "invalid_list",
    "invalid_time",
    "missing",
    "overflow",
]


SALEOR_ERROR_CODE_ENUMS = [
    AccountErrorCode,
    CheckoutErrorCode,
    ExtensionsErrorCode,
    GiftCardErrorCode,
    MenuErrorCode,
    OrderErrorCode,
    PaymentErrorCode,
    ProductErrorCode,
    ShippingErrorCode,
    ShopErrorCode,
]

saleor_error_codes = []
for enum in SALEOR_ERROR_CODE_ENUMS:
    saleor_error_codes.extend([code.value for code in enum])


def get_error_code_from_error(error):
    """Return valid error code."""
    code = error.code
    if code in ["required", "blank", "null"]:
        return "required"
    if code in ["unique", "unique_for_date"]:
        return "unique"
    if code in DJANGO_VALIDATORS_ERROR_CODES or code in DJANGO_FORM_FIELDS_ERROR_CODES:
        return "invalid"
    if isinstance(code, Enum):
        code = code.value
    if code not in saleor_error_codes:
        return "invalid"
    return code

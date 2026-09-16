import re

from app.application.exceptions import ValidationError


def normalize_phone(value: str, phone_country_code: str) -> str:
    digits = re.sub(r"\D", "", value)
    country = re.sub(r"\D", "", phone_country_code)
    if not digits or not country:
        raise ValidationError("Invalid phone number")
    if digits.startswith(country): international = digits
    elif len(digits) == 9: international = country + digits
    else: raise ValidationError("Phone must be a valid local or international number")
    if len(international) < 10 or len(international) > 15:
        raise ValidationError("Invalid phone number")
    return "+" + international

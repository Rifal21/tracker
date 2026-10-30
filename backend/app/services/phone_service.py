import logging

import phonenumbers
from phonenumbers import PhoneNumberType, geocoder, timezone

from ..config import settings
from ..schemas import PhoneInfo
from .carrier_service import detect_carrier

log = logging.getLogger("fkphone")

TYPE_NAMES = {
    PhoneNumberType.FIXED_LINE: "FIXED_LINE",
    PhoneNumberType.MOBILE: "MOBILE",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "FIXED_LINE_OR_MOBILE",
    PhoneNumberType.TOLL_FREE: "TOLL_FREE",
    PhoneNumberType.PREMIUM_RATE: "PREMIUM_RATE",
    PhoneNumberType.SHARED_COST: "SHARED_COST",
    PhoneNumberType.VOIP: "VOIP",
    PhoneNumberType.PERSONAL_NUMBER: "PERSONAL_NUMBER",
    PhoneNumberType.PAGER: "PAGER",
    PhoneNumberType.UAN: "UAN",
    PhoneNumberType.VOICEMAIL: "VOICEMAIL",
    PhoneNumberType.UNKNOWN: "UNKNOWN",
}


def mask(number: str) -> str:
    """Masking nomor untuk log: sisakan 4 digit awal dan 2 digit akhir."""
    digits = number.strip()
    if len(digits) <= 7:
        return "*" * len(digits)
    return digits[:4] + "*" * (len(digits) - 6) + digits[-2:]


def analyze(raw: str, region: str | None = None) -> PhoneInfo:
    region = (region or settings.default_region).upper()
    raw = raw.strip()
    log.info("lookup %s", mask(raw))
    try:
        num = phonenumbers.parse(raw, None if raw.startswith("+") else region)
    except phonenumbers.NumberParseException as e:
        return PhoneInfo(phone_number=raw, valid=False, possible=False, error=str(e))

    valid = phonenumbers.is_valid_number(num)
    country_iso = phonenumbers.region_code_for_number(num)
    ntype = phonenumbers.number_type(num)
    op, op_note = detect_carrier(num)
    national = phonenumbers.national_significant_number(num)
    tzs = [t for t in timezone.time_zones_for_number(num) if t != "Etc/Unknown"]
    # prefix: kode negara + 3 digit pertama nomor nasional
    prefix = f"+{num.country_code}{national[:3]}" if national else None

    return PhoneInfo(
        phone_number=phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164),
        international=phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
        national=phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL),
        country=geocoder.country_name_for_number(num, "en") or None,
        country_code=country_iso,
        calling_code=num.country_code,
        prefix=prefix,
        valid=valid,
        possible=phonenumbers.is_possible_number(num),
        number_type=TYPE_NAMES.get(ntype, "UNKNOWN"),
        carrier=op,
        carrier_note=op_note,
        region=geocoder.description_for_number(num, "en") or None,
        timezones=tzs,
    )

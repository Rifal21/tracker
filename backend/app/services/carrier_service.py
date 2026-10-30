"""Deteksi operator berdasarkan metadata prefix (phonenumbers).

Portabilitas nomor dapat membuat operator aktual berbeda dari operator prefix awal.
"""
import phonenumbers
from phonenumbers import carrier

NOTE = "Berdasarkan prefix awal; portabilitas nomor dapat membuat operator aktual berbeda."


def detect_carrier(number: phonenumbers.PhoneNumber, lang: str = "en") -> tuple[str | None, str]:
    name = carrier.name_for_number(number, lang) or None
    if name:
        return name, NOTE
    return None, "Data operator tidak tersedia untuk nomor ini."

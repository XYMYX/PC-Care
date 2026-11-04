import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Manufacturer:
    name: str
    pattern: re.Pattern
    url: str
    pc_maker_note: bool = False


MANUFACTURERS = (
    Manufacturer(
        "NVIDIA",
        re.compile(r"\bnvidia\b", re.IGNORECASE),
        "https://www.nvidia.com/en-us/drivers/",
    ),
    Manufacturer(
        "AMD",
        re.compile(r"\bamd\b|advanced micro devices", re.IGNORECASE),
        "https://www.amd.com/en/support/download/drivers.html",
    ),
    Manufacturer(
        "Intel",
        re.compile(r"\bintel\b", re.IGNORECASE),
        "https://www.intel.com/content/www/us/en/download-center/home.html",
    ),
    Manufacturer(
        "Realtek",
        re.compile(r"\brealtek\b", re.IGNORECASE),
        "https://www.realtek.com/Download/Index",
    ),
    Manufacturer(
        "Qualcomm",
        re.compile(r"\bqualcomm\b", re.IGNORECASE),
        "https://www.qualcomm.com/support",
        pc_maker_note=True,
    ),
    Manufacturer(
        "MediaTek",
        re.compile(r"\bmediatek\b", re.IGNORECASE),
        "https://www.mediatek.com/products/networking-and-connectivity",
        pc_maker_note=True,
    ),
    Manufacturer(
        "Broadcom",
        re.compile(r"\bbroadcom\b", re.IGNORECASE),
        "https://www.broadcom.com/support/download-search",
        pc_maker_note=True,
    ),
)


def find_manufacturer(provider):
    for manufacturer in MANUFACTURERS:
        if manufacturer.pattern.search(provider or ""):
            return manufacturer
    return None

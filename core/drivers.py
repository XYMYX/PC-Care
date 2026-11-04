import json
import re
from dataclasses import dataclass
from datetime import date

from core.manufacturers import Manufacturer, find_manufacturer
from core.powershell import PowerShellError, run_powershell

GRAPHICS = "graphics"
CHIPSET = "chipset"
NETWORK = "network"
AUDIO = "audio"
BLUETOOTH = "bluetooth"
CATEGORY_ORDER = (GRAPHICS, CHIPSET, NETWORK, AUDIO, BLUETOOTH)

RECENT = "recent"
OLDER = "older"
UNKNOWN = "unknown"

PLACEHOLDER_DATE = date(2006, 6, 21)
RECENT_MONTHS = 12

CLASS_RULES = {
    "DISPLAY": (GRAPHICS, ("PCI\\",)),
    "NET": (NETWORK, ("PCI\\", "USB\\", "SDIO\\")),
    "MEDIA": (AUDIO, ("HDAUDIO\\", "INTELAUDIO\\", "PCI\\", "USB\\")),
    "BLUETOOTH": (BLUETOOTH, ("USB\\", "PCI\\", "ACPI\\")),
    "SYSTEM": (CHIPSET, ("PCI\\VEN_1022", "PCI\\VEN_8086", "ACPI\\AMDI", "ACPI\\INT")),
}
CHIPSET_PROVIDER = re.compile(r"\bamd\b|advanced micro devices|\bintel\b", re.IGNORECASE)
VIRTUAL_NAME = re.compile(r"miniport|virtual|hyper-v|kernel debug|loopback|\bvpn\b|\btap\b", re.IGNORECASE)

QUERY = r"""
$classes = 'DISPLAY', 'SYSTEM', 'NET', 'MEDIA', 'BLUETOOTH'
$drivers = Get-CimInstance Win32_PnPSignedDriver |
    Where-Object { $classes -contains $_.DeviceClass } |
    ForEach-Object {
        [pscustomobject]@{
            DeviceName = $_.DeviceName
            DeviceClass = $_.DeviceClass
            DeviceID = $_.DeviceID
            Provider = $_.DriverProviderName
            Manufacturer = $_.Manufacturer
            Version = $_.DriverVersion
            Date = if ($_.DriverDate) { $_.DriverDate.ToUniversalTime().ToString('yyyy-MM-dd') } else { $null }
        }
    }
ConvertTo-Json -InputObject @($drivers) -Compress
"""


@dataclass(frozen=True)
class Driver:
    category: str
    name: str
    provider: str
    version: str
    driver_date: date | None
    status: str
    age_months: int | None
    manufacturer: Manufacturer | None


def classify(record):
    rule = CLASS_RULES.get((record.get("DeviceClass") or "").upper())
    if rule is None:
        return None
    category, id_prefixes = rule
    device_id = (record.get("DeviceID") or "").upper()
    name = record.get("DeviceName") or ""
    if not name or not device_id.startswith(id_prefixes) or VIRTUAL_NAME.search(name):
        return None
    if category == CHIPSET and not CHIPSET_PROVIDER.search(record.get("Provider") or ""):
        return None
    return category


def parse_date(value):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return None if parsed == PLACEHOLDER_DATE else parsed


def months_between(start, end):
    months = (end.year - start.year) * 12 + end.month - start.month
    if end.day < start.day:
        months -= 1
    return max(months, 0)


def build_driver(record, category, today):
    driver_date = parse_date(record.get("Date"))
    age_months = None if driver_date is None else months_between(driver_date, today)
    if age_months is None:
        status = UNKNOWN
    elif age_months < RECENT_MONTHS:
        status = RECENT
    else:
        status = OLDER
    provider = record.get("Provider") or record.get("Manufacturer") or ""
    return Driver(
        category=category,
        name=record["DeviceName"].strip(),
        provider=provider.strip(),
        version=(record.get("Version") or "").strip(),
        driver_date=driver_date,
        status=status,
        age_months=age_months,
        manufacturer=find_manufacturer(provider),
    )


def select_drivers(records, today=None):
    today = today or date.today()
    unique = {}
    for record in records:
        category = classify(record)
        if category is None:
            continue
        driver = build_driver(record, category, today)
        unique.setdefault((driver.category, driver.name, driver.version), driver)
    return sorted(
        unique.values(),
        key=lambda driver: (CATEGORY_ORDER.index(driver.category), driver.name.lower()),
    )


def read_drivers(runner=run_powershell):
    output = runner(QUERY)
    try:
        records = json.loads(output or "[]")
    except ValueError as error:
        raise PowerShellError("invalid output") from error
    return select_drivers(records)

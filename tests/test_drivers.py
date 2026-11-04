import json
from datetime import date

import pytest

from core import drivers
from core.drivers import classify, parse_date, read_drivers, select_drivers
from core.manufacturers import MANUFACTURERS, find_manufacturer
from core.powershell import PowerShellError

TODAY = date(2026, 11, 4)


def record(name="Device", device_class="NET", device_id="PCI\\VEN_10EC", provider="Realtek", day="2026-08-05"):
    return {
        "DeviceName": name,
        "DeviceClass": device_class,
        "DeviceID": device_id,
        "Provider": provider,
        "Manufacturer": "Microsoft",
        "Version": "1.0",
        "Date": day,
    }


@pytest.mark.parametrize(
    "item",
    [
        record("WAN Miniport (IP)", device_id="SWD\\MSRRAS\\MS_NDISWANIP", provider="Microsoft"),
        record("Hyper-V Virtual Switch Extension Adapter", device_id="ROOT\\VMS_VSMP\\0000"),
        record("Microsoft Kernel Debug Network Adapter", device_id="ROOT\\KDNIC\\0000"),
        record("Virtual Adapter", device_id="PCI\\VEN_1234"),
        record("Bluetooth Device (Personal Area Network)", device_id="BTH\\MS_BTHPAN\\1"),
        record("NVIDIA Virtual Audio Device", "MEDIA", "ROOT\\UNNAMED_DEVICE\\0000", "NVIDIA"),
        record("SteelSeries Sonar Virtual Audio Device", "MEDIA", "ROOT\\MEDIA\\0000", "SteelSeries ApS"),
        record("AMD Crash Defender", "SYSTEM", "ROOT\\AMDLOG\\0000", "Advanced Micro Devices, Inc."),
        record("PCI Express Root Port", "SYSTEM", "PCI\\VEN_1022&DEV_14DB", "Microsoft"),
        record("Foreign Bridge", "SYSTEM", "PCI\\VEN_1B21&DEV_1242", "ASMedia"),
        record("Speakers", "AUDIOENDPOINT", "SWD\\MMDEVAPI\\0", "Microsoft"),
    ],
)
def test_hidden_devices(item):
    assert classify(item) is None


@pytest.mark.parametrize(
    ("item", "category"),
    [
        (record("NVIDIA GeForce", "DISPLAY", "PCI\\VEN_10DE", "NVIDIA"), "graphics"),
        (record("Realtek 2.5GbE"), "network"),
        (record("USB Wi-Fi", device_id="USB\\VID_0BDA"), "network"),
        (record("Realtek Audio", "MEDIA", "HDAUDIO\\FUNC_01", "Realtek"), "audio"),
        (record("Realtek Bluetooth", "BLUETOOTH", "USB\\VID_0BDA", "Realtek"), "bluetooth"),
        (record("AMD SMBUS", "SYSTEM", "PCI\\VEN_1022&DEV_790B", "Advanced Micro Devices, Inc"), "chipset"),
        (record("AMD GPIO", "SYSTEM", "ACPI\\AMDI0030\\0", "Advanced Micro Devices, Inc"), "chipset"),
        (record("Intel SMBus", "SYSTEM", "PCI\\VEN_8086&DEV_7A23", "Intel"), "chipset"),
        (record("Intel Serial IO", "SYSTEM", "ACPI\\INT34C5\\0", "Intel Corporation"), "chipset"),
    ],
)
def test_visible_devices(item, category):
    assert classify(item) == category


@pytest.mark.parametrize(
    ("day", "status", "age"),
    [
        ("2026-11-04", "recent", 0),
        ("2026-05-26", "recent", 5),
        ("2025-11-05", "recent", 11),
        ("2025-11-04", "older", 12),
        ("2022-06-22", "older", 52),
        ("2006-06-21", "unknown", None),
        (None, "unknown", None),
        ("not a date", "unknown", None),
        ("2030-01-01", "recent", 0),
    ],
)
def test_status_from_date(day, status, age):
    driver = select_drivers([record(day=day)], TODAY)[0]
    assert driver.status == status
    assert driver.age_months == age


def test_placeholder_is_not_a_date():
    assert parse_date("2006-06-21") is None
    assert parse_date("2006-06-22") == date(2006, 6, 22)


def test_duplicates_are_merged():
    items = [
        record("AMD I2C Controller", "SYSTEM", "ACPI\\AMDI0010\\0", "AMD"),
        record("AMD I2C Controller", "SYSTEM", "ACPI\\AMDI0010\\1", "AMD"),
    ]
    assert len(select_drivers(items, TODAY)) == 1


def test_sorted_by_category_then_name():
    items = [
        record("Zeta"),
        record("Alpha"),
        record("GPU", "DISPLAY", "PCI\\VEN_10DE", "NVIDIA"),
    ]
    assert [driver.name for driver in select_drivers(items, TODAY)] == ["GPU", "Alpha", "Zeta"]


def test_provider_wins_over_manufacturer_field():
    item = record("Realtek High Definition Audio", "MEDIA", "HDAUDIO\\FUNC_01", "Realtek Semiconductor Corp.")
    driver = select_drivers([item], TODAY)[0]
    assert driver.provider == "Realtek Semiconductor Corp."
    assert driver.manufacturer.name == "Realtek"


def test_missing_provider_uses_manufacturer_field():
    item = record(provider=None)
    assert select_drivers([item], TODAY)[0].provider == "Microsoft"


@pytest.mark.parametrize(
    ("provider", "name"),
    [
        ("NVIDIA", "NVIDIA"),
        ("NVIDIA Corporation", "NVIDIA"),
        ("Advanced Micro Devices, Inc.", "AMD"),
        ("AMD", "AMD"),
        ("Intel Corporation", "Intel"),
        ("Realtek Semiconductor Corp.", "Realtek"),
        ("Qualcomm Atheros", "Qualcomm"),
        ("MediaTek, Inc.", "MediaTek"),
        ("Broadcom", "Broadcom"),
    ],
)
def test_known_manufacturers(provider, name):
    assert find_manufacturer(provider).name == name


@pytest.mark.parametrize("provider", ["Microsoft", "SteelSeries ApS", "", None, "Intelligent Devices", "Samdata"])
def test_unknown_manufacturer_has_no_link(provider):
    assert find_manufacturer(provider) is None


def test_all_links_are_official_https():
    domains = {
        "NVIDIA": "www.nvidia.com",
        "AMD": "www.amd.com",
        "Intel": "www.intel.com",
        "Realtek": "www.realtek.com",
        "Qualcomm": "www.qualcomm.com",
        "MediaTek": "www.mediatek.com",
        "Broadcom": "www.broadcom.com",
    }
    assert {manufacturer.name for manufacturer in MANUFACTURERS} == set(domains)
    for manufacturer in MANUFACTURERS:
        assert manufacturer.url.startswith(f"https://{domains[manufacturer.name]}/")


def test_read_drivers_uses_runner():
    output = json.dumps([record("Realtek 2.5GbE")])
    assert [driver.name for driver in read_drivers(lambda _query: output)] == ["Realtek 2.5GbE"]


def test_read_drivers_rejects_invalid_output():
    with pytest.raises(PowerShellError):
        read_drivers(lambda _query: "not json")


def test_read_drivers_handles_empty_output():
    assert read_drivers(lambda _query: "") == []


def test_query_uses_utc_date():
    assert "ToUniversalTime()" in drivers.QUERY

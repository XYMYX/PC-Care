from datetime import date

import pytest

from core.texts import TEXTS, format_age, format_date, text


def test_languages_have_the_same_keys():
    assert set(TEXTS["de"]) == set(TEXTS["en"])


@pytest.mark.parametrize(
    ("language", "months", "expected"),
    [
        ("en", None, "Unknown"),
        ("de", None, "Unbekannt"),
        ("en", 0, "under 1 month"),
        ("en", 1, "1 month"),
        ("de", 5, "5 Monate"),
        ("en", 12, "1 year"),
        ("de", 13, "1 Jahr, 1 Monat"),
        ("en", 52, "4 years, 4 months"),
    ],
)
def test_format_age(language, months, expected):
    assert format_age(language, months) == expected


def test_format_date():
    assert format_date("de", date(2026, 3, 9)) == "09.03.2026"
    assert format_date("en", date(2026, 3, 9)) == "2026-03-09"
    assert format_date("en", None) == "Unknown"


def test_unknown_language_falls_back_to_english():
    assert text("fr", "back") == "Back"

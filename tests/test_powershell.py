import pytest

from core.powershell import PowerShellError, run_powershell


def test_returns_utf8_output():
    assert run_powershell("Write-Output 'Grüße'").strip() == "Grüße"


def test_failure_raises():
    with pytest.raises(PowerShellError):
        run_powershell("exit 3")


def test_timeout_raises():
    with pytest.raises(PowerShellError):
        run_powershell("Start-Sleep -Seconds 30", timeout=1)

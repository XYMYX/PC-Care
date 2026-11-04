from pathlib import Path

from core.admin import parse_options, restart_as_admin, restart_command


def test_frozen_restart_uses_only_the_exe():
    program, parameters = restart_command("C:/S F", "Anna", frozen=True, executable="C:/App/care.exe")
    assert program == "C:/App/care.exe"
    assert parameters == '--settings-folder "C:/S F" --original-user Anna'


def test_source_restart_uses_python_and_script(tmp_path):
    python = tmp_path / "python.exe"
    (tmp_path / "pythonw.exe").write_text("")
    program, parameters = restart_command("C:/S", "Anna", False, python, Path("C:/my app/main.py"))
    assert program == str(tmp_path / "pythonw.exe")
    assert parameters.startswith('"C:\\my app\\main.py" --settings-folder')


def test_source_restart_falls_back_to_python(tmp_path):
    python = tmp_path / "python.exe"
    program, _parameters = restart_command("C:/S", "Anna", False, python, Path("main.py"))
    assert program == str(python)


def test_cancelled_uac_prompt_returns_false():
    assert restart_as_admin("C:/S", "Anna", launcher=lambda _program, _parameters: 5) is False


def test_started_restart_returns_true():
    assert restart_as_admin("C:/S", "Anna", launcher=lambda _program, _parameters: 42) is True


def test_parse_options():
    options = parse_options(["--settings-folder", "C:/S", "--original-user", "Anna"])
    assert options.settings_folder == "C:/S"
    assert options.original_user == "Anna"


def test_parse_options_handles_missing_values():
    assert parse_options(["--settings-folder"]).settings_folder is None
    assert parse_options([]).original_user is None

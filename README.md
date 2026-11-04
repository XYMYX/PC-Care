# XYMYX PC Care
**A simple Windows maintenance tool that only shows and suggests. Nothing happens without your OK.**

XYMYX PC Care does two things. It shows how old your most important drivers are, and it cleans temporary files and caches from a fixed list of safe places. It is made for non-technical users and family, with plain language, large buttons, and German and English text.

It runs locally on Windows 10 and 11. There is no cloud, no telemetry, and no ads. The only time it touches the internet is when you open a manufacturer page in your browser.

Written by XYMYX. Python 3.12 or newer. One runtime dependency: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

## Why this shape

- **Show first, act later.** Every cleanup starts with a preview that deletes nothing. All checkboxes start empty, and a final question names the categories, the size, and that deletion is permanent.
- **A fixed allowlist.** Files are only deleted from places listed in the code. There is no setting to add more.
- **One module deletes.** All file deletion goes through [core/deletion.py](core/deletion.py), so there is one place to read and test.
- **Honest about drivers.** The tool only looks at the driver date. It cannot check whether a newer version exists, so it never says one does.

## What it does

### Drivers (read-only)

Shows graphics card, chipset, network, audio, and Bluetooth drivers. Virtual devices such as WAN Miniports are hidden.

| Status | Meaning |
| --- | --- |
| Recent | The driver date is under 12 months old. |
| Older | The driver date is 12 months old or more. |
| Unknown | There is no date, or the date is the Windows placeholder 2006-06-21. |

A button opens the official page for NVIDIA, AMD, Intel, Realtek, Qualcomm, MediaTek, or Broadcom after you confirm. Qualcomm, MediaTek, and Broadcom usually offer no drivers for home users, so the tool points you to your PC maker instead. For other manufacturers it shows "Check manufacturer website". It downloads and installs nothing.

### Clean up

Available without admin rights:

| Category | Location |
| --- | --- |
| Temporary files | `%TEMP%`, skipping files from the last 24 hours |
| Edge and Chrome cache | Cache folders in each profile |
| Firefox cache | `cache2` and `startupCache` in each profile |
| Recycle bin | Windows API |
| Thumbnails | `thumbcache_*.db` |
| DirectX shader cache | `%LOCALAPPDATA%\D3DSCache` |
| Graphics card cache | NVIDIA and AMD shader caches in `%LOCALAPPDATA%` |
| Error reports | User Windows Error Reporting folders |

Only available after restarting the tool as administrator:

| Category | Location |
| --- | --- |
| Windows temporary files | `C:\Windows\Temp`, skipping files from the last 24 hours |
| Windows Update downloads | `C:\Windows\SoftwareDistribution\Download` |
| Windows log files | `C:\Windows\Logs` |
| Windows crash reports | `C:\Windows\Minidump` and `C:\Windows\MEMORY.DMP` |
| Delivery Optimization | Official PowerShell cmdlet |

Clearing the graphics card cache can make games load slowly or stutter once while it is rebuilt. Logs and crash reports can help with troubleshooting, so keep them if your PC is having problems.

The start screen shows the total space freed across all cleanups. This counts bytes actually deleted, not the preview estimate.

## Installation

### The .exe

Download `XYMYX-PC-Care.exe` and start it. No installation is needed.

The .exe is **unsigned**, so Windows SmartScreen may show a warning. If you trust the source, choose "More info" and then "Run anyway". You can also build it yourself from this source.

### From source

```bash
git clone https://github.com/XYMYX/PC-Care.git
cd PC-Care
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

### Build the .exe

```bash
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m PyInstaller xymyx_pc_care.spec
```

The result is `dist\XYMYX-PC-Care.exe`.

## Usage

1. Start the tool. It uses German if Windows is set to German, otherwise English. You can switch on the start screen.
2. Choose **Drivers** to see how old your drivers are.
3. Choose **Clean up** to see how much space can be freed.
4. Tick what can go, then choose **Delete selected** and confirm.
5. To reach the Windows categories, choose **Restart as administrator** and accept the Windows prompt. If you say no, the tool carries on as normal.

A browser cache can only be cleaned when that browser is closed. Edge can keep running in the background. Windows Update downloads are skipped while Windows Update or TrustedInstaller is running, because cleaning them could damage an update in progress.

Files in use or without permission are skipped and counted.

The tool also works without a mouse. Tab moves between items, Enter or Space activates them, and Esc closes a question. In a question, the safe answer is selected first.

Only one window runs at a time. Starting the tool again brings the open window to the front.

Settings and the freed-space counter are saved in `%APPDATA%\XYMYX PC Care\settings.json`. Every cleanup is logged in `log.txt` in the same folder. The log keeps its newest entries and stays under about 1 MB.

## Project structure

```
XYMYX-PC-CARE/
├─ main.py                    starts the app
├─ xymyx_pc_care.spec         PyInstaller build
├─ core/
│  ├─ activity_log.py         log.txt
│  ├─ admin.py                admin check and restart
│  ├─ categories.py           the fixed allowlist
│  ├─ cleanup.py              preview and cleanup flow
│  ├─ deletion.py             the only module that deletes files
│  ├─ drivers.py              driver query, filter, status
│  ├─ manufacturers.py        fixed list of official URLs
│  ├─ powershell.py           hidden PowerShell with a timeout
│  ├─ settings.py             settings, counter, size format
│  ├─ single_instance.py      keeps it to one running window
│  ├─ texts.py                all German and English text
│  └─ windows_cleanup.py      recycle bin, Delivery Optimization, system state
├─ ui/                        start, driver, and cleanup screens
├─ assets/                    program icon
├─ tools/make_icon.py         draws the icon from the logo lines
└─ tests/                     pytest suite
```

## Security principles

- **Starts without admin rights.** The .exe has no UAC manifest. Admin rights are only requested after you confirm.
- **Path checks before every deletion.** The real path is resolved and must be inside an allowlisted root. Anything else is refused and logged.
- **Links are never followed.** Symlinks, junctions, and other reparse points are not entered. At most the link itself is removed, never its target.
- **Root folders stay.** Only the contents of a folder are deleted.
- **Never touched:** Prefetch, WinSxS, Windows.old, `hiberfil.sys`, `pagefile.sys`, the registry, and system files. Browser cookies, history, passwords, bookmarks, extensions, sessions, and settings also stay.
- **Windows is left running.** No services are stopped or changed, and Explorer is never restarted. Locked files are skipped.
- **No third-party driver sites.** Links are hardcoded to official manufacturer sites.
- **Safe when unsure.** If the tool cannot tell whether a browser or Windows Update is running, it assumes yes and skips that category.
- **A broken `TEMP` setting is ignored.** If `TEMP` does not look like a temp folder, or points into Windows, that category is unavailable.

Deletion is permanent. Read the preview before you confirm.

## Tests

```bash
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest
```

Deletion tests run only on temporary dummy folders. They cover paths outside the allowlist, junctions pointing outside the test folder, locked files, and empty folders. One symlink test needs Developer Mode or admin rights and is skipped otherwise.

## How it was made

- **Idea, requirements, and testing:** me
- **Code:** written by AI (Claude) based on my requirements

I'm still learning to code, so this is not my handwritten code. I'm open about that.

## License

MIT. Copyright (c) 2026 XYMYX. See [LICENSE](LICENSE).

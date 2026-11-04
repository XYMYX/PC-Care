LANGUAGES = {"de": "Deutsch", "en": "English"}
DEFAULT_LANGUAGE = "en"

TEXTS = {
    "de": {
        "app_title": "XYMYX PC Care",
        "start_intro": "Dein PC im Blick. Es passiert nichts ohne deine Zustimmung.",
        "tile_drivers": "Treiber",
        "tile_drivers_hint": "Zeigt, wie alt deine Treiber sind",
        "tile_cleanup": "Aufräumen",
        "tile_cleanup_hint": "Zeigt, wie viel Platz frei werden kann",
        "freed_total": "Bisher freigegeben: {size}",
        "back": "Zurück",
        "drivers_title": "Treiber-Übersicht",
        "drivers_intro": (
            "Hier siehst du, wie alt deine wichtigsten Treiber sind. "
            "Das Programm kann nicht prüfen, ob es neuere Versionen gibt."
        ),
        "drivers_loading": "Treiber werden gelesen. Das dauert einen Moment ...",
        "drivers_empty": "Es wurden keine passenden Treiber gefunden.",
        "drivers_error": "Die Treiber konnten nicht gelesen werden.",
        "drivers_rescan": "Neu einlesen",
        "category_graphics": "Grafikkarte",
        "category_chipset": "Chipsatz",
        "category_network": "Netzwerk (LAN/WLAN)",
        "category_audio": "Audio",
        "category_bluetooth": "Bluetooth",
        "status_recent": "Neu",
        "status_older": "Älter",
        "status_unknown": "Unbekannt",
        "field_manufacturer": "Hersteller",
        "field_version": "Version",
        "field_date": "Treiberdatum",
        "field_age": "Alter",
        "value_unknown": "Unbekannt",
        "age_under_month": "unter 1 Monat",
        "age_month_one": "1 Monat",
        "age_months": "{count} Monate",
        "age_year_one": "1 Jahr",
        "age_years": "{count} Jahre",
        "open_driver_page": "Treiberseite des Herstellers öffnen",
        "check_manufacturer": "Bitte auf der Website des Herstellers nachsehen",
        "pc_maker_note": (
            "Dieser Hersteller bietet meist keine Treiber für Privatpersonen an. "
            "Schau am besten auf der Website deines PC-Herstellers nach."
        ),
        "open_page_title": "Website öffnen?",
        "open_page_body": (
            "Dein Browser öffnet jetzt die offizielle Seite von {manufacturer}:\n\n"
            "{url}\n\n"
            "Dieses Programm lädt nichts herunter und installiert nichts."
        ),
        "confirm_open": "Seite öffnen",
        "cancel": "Abbrechen",
        "cleanup_title": "Aufräumen",
        "cleanup_intro": (
            "Das ist nur eine Vorschau, noch wird nichts gelöscht. "
            "Wähle aus, was weg darf. Danach fragen wir noch einmal nach."
        ),
        "scan_loading": "Dein PC wird geprüft. Dabei wird nichts gelöscht ...",
        "scan_rescan": "Neu prüfen",
        "scan_error": "Die Prüfung hat nicht geklappt. Bitte versuche es noch einmal.",
        "section_user": "Das kannst du direkt aufräumen",
        "section_admin": "Nur mit Administratorrechten",
        "section_admin_hint": (
            "Diese Bereiche gehören zu Windows. "
            "Du kannst sie erst auswählen, wenn du das Programm als Administrator neu startest."
        ),
        "section_admin_active": "Das Programm läuft gerade mit Administratorrechten. Bitte wähle hier besonders sorgfältig aus.",
        "section_other_account": (
            "Du hast dich mit einem anderen Konto angemeldet. "
            "Darum sind die persönlichen Bereiche jetzt ausgeblendet."
        ),
        "admin_restart": "Als Administrator neu starten",
        "admin_restart_title": "Als Administrator neu starten?",
        "admin_restart_body": (
            "Das Programm schließt sich und startet neu. "
            "Windows fragt dich dabei um Erlaubnis.\n\n"
            "Es wird noch nichts gelöscht. Wenn du bei Windows ablehnst, läuft alles normal weiter."
        ),
        "admin_restart_confirm": "Neu starten",
        "admin_restart_cancelled": "Kein Neustart. Du kannst normal weitermachen.",
        "selected_total": "Ausgewählt: {size}",
        "clean_button": "Ausgewähltes löschen",
        "confirm_clean_title": "Wirklich endgültig löschen?",
        "confirm_clean_body": (
            "Das wird gelöscht:\n\n{names}\n\n"
            "Zusammen etwa {size}.\n\n"
            "Das Löschen ist endgültig. Du kannst diese Dateien nicht wiederherstellen."
        ),
        "confirm_clean_action": "Endgültig löschen",
        "cleaning": "Es wird aufgeräumt. Bitte lass das Programm offen ...",
        "result_title": "Fertig",
        "result_freed": "Freigegeben: {size}",
        "result_skipped": "Übersprungene Dateien: {count}",
        "result_skipped_hint": "Diese Dateien waren gerade in Benutzung oder geschützt. Das ist normal.",
        "result_not_cleaned": "Nicht aufgeräumt:",
        "result_back": "Zur Übersicht",
        "status_empty": "Nichts zum Aufräumen",
        "status_not_installed": "Auf diesem PC nicht vorhanden",
        "status_close_browser": "Bitte schließe zuerst {browser}.",
        "status_close_edge": "Bitte schließe zuerst Edge. Edge kann auch im Hintergrund weiterlaufen.",
        "status_needs_admin": "Braucht Administratorrechte",
        "status_other_account": "Gehört zu einem anderen Konto",
        "status_update_running": (
            "Windows Update ist gerade aktiv. Damit kein Update beschädigt wird, "
            "bleibt dieser Ordner unberührt. Versuche es später noch einmal."
        ),
        "status_failed": "Hat nicht geklappt",
        "cat_user_temp": "Temporäre Dateien",
        "cat_user_temp_hint": "Reste von Programmen. Dateien der letzten 24 Stunden bleiben erhalten.",
        "cat_edge": "Edge-Zwischenspeicher",
        "cat_edge_hint": "Gespeicherte Teile von Websites. Passwörter, Verlauf und Lesezeichen bleiben erhalten.",
        "cat_chrome": "Chrome-Zwischenspeicher",
        "cat_chrome_hint": "Gespeicherte Teile von Websites. Passwörter, Verlauf und Lesezeichen bleiben erhalten.",
        "cat_firefox": "Firefox-Zwischenspeicher",
        "cat_firefox_hint": "Gespeicherte Teile von Websites. Passwörter, Verlauf und Lesezeichen bleiben erhalten.",
        "cat_recycle_bin": "Papierkorb",
        "cat_recycle_bin_hint": "Alles im Papierkorb wird endgültig gelöscht. Schau am besten vorher hinein.",
        "cat_thumbnails": "Vorschaubilder",
        "cat_thumbnails_hint": "Kleine Bilder im Explorer. Windows erstellt sie bei Bedarf neu.",
        "cat_directx_shader": "DirectX-Shader-Speicher",
        "cat_directx_shader_hint": "Vorbereitete Grafikdaten von Windows. Sie werden bei Bedarf neu erstellt.",
        "cat_gpu_shader": "Grafikkarten-Speicher (NVIDIA/AMD)",
        "cat_gpu_shader_hint": (
            "Vorbereitete Grafikdaten für Spiele. Danach können Spiele einmal "
            "länger laden oder kurz ruckeln, bis alles neu erstellt ist."
        ),
        "cat_error_reports": "Fehlerberichte",
        "cat_error_reports_hint": "Berichte über abgestürzte Programme. Sie werden sonst nicht mehr gebraucht.",
        "cat_windows_temp": "Temporäre Windows-Dateien",
        "cat_windows_temp_hint": "Reste von Windows. Dateien der letzten 24 Stunden bleiben erhalten.",
        "cat_windows_update": "Windows-Update-Downloads",
        "cat_windows_update_hint": "Bereits geladene Update-Dateien. Windows lädt sie bei Bedarf neu.",
        "cat_windows_logs": "Windows-Protokolle",
        "cat_windows_logs_hint": (
            "Aufzeichnungen darüber, was Windows getan hat. Sie können bei der Fehlersuche "
            "helfen. Lösche sie nicht, wenn dein PC gerade Probleme macht."
        ),
        "cat_crash_dumps": "Absturzberichte von Windows",
        "cat_crash_dumps_hint": (
            "Dateien von früheren Bluescreens. Sie zeigen, warum der PC abgestürzt ist. "
            "Lösche sie nicht, wenn du einen Absturz noch untersuchen möchtest."
        ),
        "cat_delivery_optimization": "Übermittlungsoptimierung",
        "cat_delivery_optimization_hint": "Update-Dateien, die Windows mit anderen PCs teilen kann.",
    },
    "en": {
        "app_title": "XYMYX PC Care",
        "start_intro": "Keep an eye on your PC. Nothing happens without your OK.",
        "tile_drivers": "Drivers",
        "tile_drivers_hint": "Shows how old your drivers are",
        "tile_cleanup": "Clean up",
        "tile_cleanup_hint": "Shows how much space can be freed",
        "freed_total": "Freed so far: {size}",
        "back": "Back",
        "drivers_title": "Driver overview",
        "drivers_intro": (
            "This shows how old your most important drivers are. "
            "The tool cannot check whether newer versions exist."
        ),
        "drivers_loading": "Reading drivers. This takes a moment ...",
        "drivers_empty": "No matching drivers were found.",
        "drivers_error": "The drivers could not be read.",
        "drivers_rescan": "Read again",
        "category_graphics": "Graphics card",
        "category_chipset": "Chipset",
        "category_network": "Network (LAN/Wi-Fi)",
        "category_audio": "Audio",
        "category_bluetooth": "Bluetooth",
        "status_recent": "Recent",
        "status_older": "Older",
        "status_unknown": "Unknown",
        "field_manufacturer": "Manufacturer",
        "field_version": "Version",
        "field_date": "Driver date",
        "field_age": "Age",
        "value_unknown": "Unknown",
        "age_under_month": "under 1 month",
        "age_month_one": "1 month",
        "age_months": "{count} months",
        "age_year_one": "1 year",
        "age_years": "{count} years",
        "open_driver_page": "Open manufacturer driver page",
        "check_manufacturer": "Check manufacturer website",
        "pc_maker_note": (
            "This manufacturer usually offers no drivers for home users. "
            "Your PC maker's website is the best place to look."
        ),
        "open_page_title": "Open website?",
        "open_page_body": (
            "Your browser will open the official {manufacturer} page:\n\n"
            "{url}\n\n"
            "This tool downloads nothing and installs nothing."
        ),
        "confirm_open": "Open page",
        "cancel": "Cancel",
        "cleanup_title": "Clean up",
        "cleanup_intro": (
            "This is only a preview, nothing is deleted yet. "
            "Choose what can go. You will be asked once more before anything happens."
        ),
        "scan_loading": "Checking your PC. Nothing is deleted ...",
        "scan_rescan": "Check again",
        "scan_error": "The check did not work. Please try again.",
        "section_user": "You can clean these right away",
        "section_admin": "Needs administrator rights",
        "section_admin_hint": (
            "These areas belong to Windows. "
            "You can only choose them after restarting the tool as administrator."
        ),
        "section_admin_active": "The tool is running with administrator rights. Please choose carefully here.",
        "section_other_account": (
            "You signed in with a different account, "
            "so the personal areas are hidden for now."
        ),
        "admin_restart": "Restart as administrator",
        "admin_restart_title": "Restart as administrator?",
        "admin_restart_body": (
            "The tool will close and start again. "
            "Windows will ask for your permission.\n\n"
            "Nothing is deleted yet. If you say no in Windows, everything carries on as normal."
        ),
        "admin_restart_confirm": "Restart",
        "admin_restart_cancelled": "No restart. You can carry on as normal.",
        "selected_total": "Selected: {size}",
        "clean_button": "Delete selected",
        "confirm_clean_title": "Delete permanently?",
        "confirm_clean_body": (
            "This will be deleted:\n\n{names}\n\n"
            "About {size} in total.\n\n"
            "Deletion is permanent. You cannot get these files back."
        ),
        "confirm_clean_action": "Delete permanently",
        "cleaning": "Cleaning up. Please keep the tool open ...",
        "result_title": "Done",
        "result_freed": "Freed: {size}",
        "result_skipped": "Skipped files: {count}",
        "result_skipped_hint": "These files were in use or protected. That is normal.",
        "result_not_cleaned": "Not cleaned:",
        "result_back": "Back to overview",
        "status_empty": "Nothing to clean",
        "status_not_installed": "Not on this PC",
        "status_close_browser": "Please close {browser} first.",
        "status_close_edge": "Please close Edge first. Edge can keep running in the background.",
        "status_needs_admin": "Needs administrator rights",
        "status_other_account": "Belongs to a different account",
        "status_update_running": (
            "Windows Update is active right now. To avoid damaging an update, "
            "this folder is left alone. Please try again later."
        ),
        "status_failed": "Did not work",
        "cat_user_temp": "Temporary files",
        "cat_user_temp_hint": "Leftovers from programs. Files from the last 24 hours are kept.",
        "cat_edge": "Edge cache",
        "cat_edge_hint": "Saved parts of websites. Passwords, history and bookmarks are kept.",
        "cat_chrome": "Chrome cache",
        "cat_chrome_hint": "Saved parts of websites. Passwords, history and bookmarks are kept.",
        "cat_firefox": "Firefox cache",
        "cat_firefox_hint": "Saved parts of websites. Passwords, history and bookmarks are kept.",
        "cat_recycle_bin": "Recycle bin",
        "cat_recycle_bin_hint": "Everything in the recycle bin is deleted for good. Have a look inside first.",
        "cat_thumbnails": "Thumbnails",
        "cat_thumbnails_hint": "Small pictures in File Explorer. Windows makes new ones when needed.",
        "cat_directx_shader": "DirectX shader cache",
        "cat_directx_shader_hint": "Prepared graphics data from Windows. It is rebuilt when needed.",
        "cat_gpu_shader": "Graphics card cache (NVIDIA/AMD)",
        "cat_gpu_shader_hint": (
            "Prepared graphics data for games. Afterwards games may load slowly "
            "or stutter once while it is rebuilt."
        ),
        "cat_error_reports": "Error reports",
        "cat_error_reports_hint": "Reports about crashed programs. They are not needed any more.",
        "cat_windows_temp": "Windows temporary files",
        "cat_windows_temp_hint": "Leftovers from Windows. Files from the last 24 hours are kept.",
        "cat_windows_update": "Windows Update downloads",
        "cat_windows_update_hint": "Update files already downloaded. Windows gets them again if needed.",
        "cat_windows_logs": "Windows log files",
        "cat_windows_logs_hint": (
            "Records of what Windows has been doing. They can help with troubleshooting. "
            "Do not delete them if your PC is having problems."
        ),
        "cat_crash_dumps": "Windows crash reports",
        "cat_crash_dumps_hint": (
            "Files from past blue screens. They show why the PC crashed. "
            "Do not delete them if you still want to look into a crash."
        ),
        "cat_delivery_optimization": "Delivery Optimization",
        "cat_delivery_optimization_hint": "Update files that Windows can share with other PCs.",
    },
}


def text(language, key, **values):
    template = TEXTS.get(language, TEXTS[DEFAULT_LANGUAGE])[key]
    return template.format(**values) if values else template


def format_age(language, months):
    if months is None:
        return text(language, "value_unknown")
    if months < 1:
        return text(language, "age_under_month")
    years, rest = divmod(months, 12)
    parts = []
    if years == 1:
        parts.append(text(language, "age_year_one"))
    elif years > 1:
        parts.append(text(language, "age_years", count=years))
    if rest == 1:
        parts.append(text(language, "age_month_one"))
    elif rest > 1:
        parts.append(text(language, "age_months", count=rest))
    return ", ".join(parts)


def format_date(language, value):
    if value is None:
        return text(language, "value_unknown")
    return value.strftime("%d.%m.%Y" if language == "de" else "%Y-%m-%d")

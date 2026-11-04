import tkinter
import webbrowser

import customtkinter as ctk

from core.drivers import CATEGORY_ORDER, read_drivers
from core.texts import format_age, format_date, text
from ui import theme
from ui.background import run_in_background
from ui.dialogs import confirm

BODY_WRAP = 960


class DriverScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.WHITE)
        self.app = app
        self.language = app.language

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=40, pady=(30, 0))
        theme.secondary_button(top, text(self.language, "back"), app.show_start).pack(side="left")
        ctk.CTkLabel(
            top,
            text=text(self.language, "drivers_title"),
            font=theme.font(28, "bold"),
            text_color=theme.TEXT,
        ).pack(side="left", padx=24)
        self.rescan_button = theme.secondary_button(top, text(self.language, "drivers_rescan"), self.scan)
        self.rescan_button.pack(side="right")

        ctk.CTkLabel(
            self,
            text=text(self.language, "drivers_intro"),
            font=theme.font(18),
            text_color=theme.MUTED,
            wraplength=BODY_WRAP,
            justify="left",
        ).pack(anchor="w", padx=40, pady=(18, 12))

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=(40, 24), pady=(0, 24))
        self.scan()

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def scan(self):
        self.clear_content()
        self.rescan_button.configure(state="disabled")
        ctk.CTkLabel(
            self.content,
            text=text(self.language, "drivers_loading"),
            font=theme.font(20),
            text_color=theme.TEXT,
        ).pack(pady=(60, 16))
        progress = ctk.CTkProgressBar(
            self.content, mode="indeterminate", width=420, progress_color=theme.PRIMARY
        )
        progress.pack()
        progress.start()
        run_in_background(self, read_drivers, self.show_drivers, self.show_error)

    def show_error(self, _error):
        self.show_message("drivers_error")

    def show_message(self, key):
        self.clear_content()
        self.rescan_button.configure(state="normal")
        ctk.CTkLabel(
            self.content,
            text=text(self.language, key),
            font=theme.font(20),
            text_color=theme.TEXT,
        ).pack(pady=60)

    def show_drivers(self, drivers):
        if not drivers:
            self.show_message("drivers_empty")
            return
        self.clear_content()
        self.rescan_button.configure(state="normal")
        rows = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        rows.pack(fill="both", expand=True)
        for category in CATEGORY_ORDER:
            matching = [driver for driver in drivers if driver.category == category]
            if not matching:
                continue
            ctk.CTkLabel(
                rows,
                text=text(self.language, f"category_{category}"),
                font=theme.font(22, "bold"),
                text_color=theme.TEXT,
            ).pack(anchor="w", pady=(16, 8))
            for driver in matching:
                self.add_driver_card(rows, driver)

    def add_driver_card(self, parent, driver):
        language = self.language
        card = ctk.CTkFrame(
            parent, fg_color=theme.SURFACE, border_color=theme.BORDER, border_width=1, corner_radius=12
        )
        card.pack(fill="x", pady=(0, 10), padx=(0, 12))

        heading = ctk.CTkFrame(card, fg_color="transparent")
        heading.pack(fill="x", padx=18, pady=(14, 4))
        ctk.CTkLabel(
            heading,
            text=driver.name,
            font=theme.font(19, "bold"),
            text_color=theme.TEXT,
            wraplength=720,
            justify="left",
        ).pack(side="left")
        background, foreground = theme.STATUS_COLORS[driver.status]
        ctk.CTkLabel(
            heading,
            text=text(language, f"status_{driver.status}"),
            font=theme.font(16, "bold"),
            fg_color=background,
            text_color=foreground,
            corner_radius=8,
            height=32,
            padx=14,
        ).pack(side="right")

        details = "     ".join(
            (
                f"{text(language, 'field_manufacturer')}: {driver.provider or text(language, 'value_unknown')}",
                f"{text(language, 'field_version')}: {driver.version or text(language, 'value_unknown')}",
            )
        )
        dates = "     ".join(
            (
                f"{text(language, 'field_date')}: {format_date(language, driver.driver_date)}",
                f"{text(language, 'field_age')}: {format_age(language, driver.age_months)}",
            )
        )
        ctk.CTkLabel(
            card,
            text=f"{details}\n{dates}",
            font=theme.font(17),
            text_color=theme.TEXT,
            wraplength=BODY_WRAP - 60,
            justify="left",
        ).pack(anchor="w", padx=18)

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=18, pady=(8, 14))
        manufacturer = driver.manufacturer
        if manufacturer is None:
            ctk.CTkLabel(
                footer,
                text=text(language, "check_manufacturer"),
                font=theme.font(17),
                text_color=theme.MUTED,
            ).pack(anchor="w")
            return
        open_button = theme.secondary_button(
            footer,
            text(language, "open_driver_page"),
            lambda: self.open_page(manufacturer),
        )
        open_button.pack(anchor="w")
        tkinter.Misc.bind(
            open_button,
            "<FocusIn>",
            lambda _event: theme.scroll_into_view(parent, card),
            add="+",
        )
        if manufacturer.pc_maker_note:
            ctk.CTkLabel(
                footer,
                text=text(language, "pc_maker_note"),
                font=theme.font(16),
                text_color=theme.MUTED,
                wraplength=BODY_WRAP - 60,
                justify="left",
            ).pack(anchor="w", pady=(6, 0))

    def open_page(self, manufacturer):
        confirmed = confirm(
            self.app,
            text(self.language, "open_page_title"),
            text(
                self.language,
                "open_page_body",
                manufacturer=manufacturer.name,
                url=manufacturer.url,
            ),
            text(self.language, "confirm_open"),
            text(self.language, "cancel"),
        )
        if confirmed:
            webbrowser.open(manufacturer.url)

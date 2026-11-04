import tkinter
import webbrowser

import customtkinter as ctk

from core.drivers import CATEGORY_ORDER, OLDER, UNKNOWN, read_drivers
from core.texts import format_age, format_date, text
from ui import theme
from ui.background import run_in_background
from ui.dialogs import confirm

BODY_WRAP = 1000
NAME_WRAP = 270
COLUMN_WIDTHS = ((1, 300), (0, 120), (0, 195), (0, 135), (0, 215))
OLDER_ROW_BORDER = "#7A6228"


def set_columns(frame):
    scaling = ctk.ScalingTracker.get_widget_scaling(frame)
    for column, (weight, width) in enumerate(COLUMN_WIDTHS):
        frame.grid_columnconfigure(column, weight=weight, minsize=round(width * scaling))


class DriverScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.BACKGROUND)
        self.app = app
        self.language = app.language

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=40, pady=(30, 0))
        theme.title_label(top, text(self.language, "drivers_title")).pack(side="left")
        theme.secondary_button(top, f"< {text(self.language, 'back')}", app.show_start).pack(side="right")
        self.rescan_button = theme.secondary_button(top, text(self.language, "drivers_rescan"), self.scan)
        self.rescan_button.pack(side="right", padx=(0, 12))

        self.status = ctk.CTkLabel(
            self,
            text="",
            font=theme.font(17),
            text_color=theme.MUTED,
            wraplength=BODY_WRAP,
            justify="left",
        )
        self.status.pack(anchor="w", padx=40, pady=(16, 8))

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=(40, 24), pady=(0, 16))

        ctk.CTkLabel(
            self,
            text=text(self.language, "drivers_intro"),
            font=theme.font(16),
            text_color=theme.MUTED,
            wraplength=BODY_WRAP,
            justify="left",
        ).pack(anchor="w", padx=40, pady=(0, 18))
        self.scan()

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def scan(self):
        self.clear_content()
        self.rescan_button.configure(state="disabled")
        self.status.configure(text=f"> {text(self.language, 'drivers_loading')}")
        progress = theme.progress_bar(self.content, "indeterminate")
        progress.pack(pady=60)
        progress.start()
        run_in_background(self, read_drivers, self.show_drivers, self.show_error)

    def show_error(self, _error):
        self.show_message("drivers_error")

    def show_message(self, key):
        self.clear_content()
        self.rescan_button.configure(state="normal")
        self.status.configure(text=f"> {text(self.language, key)}")

    def summary(self, drivers):
        return text(
            self.language,
            "drivers_summary",
            total=len(drivers),
            older=sum(driver.status == OLDER for driver in drivers),
            unknown=sum(driver.status == UNKNOWN for driver in drivers),
        )

    def show_drivers(self, drivers):
        if not drivers:
            self.show_message("drivers_empty")
            return
        self.clear_content()
        self.rescan_button.configure(state="normal")
        self.status.configure(
            text=f"> {text(self.language, 'drivers_done')}\n> {self.summary(drivers)} █"
        )
        rows = theme.scrollable_frame(self.content)
        rows.pack(fill="both", expand=True)
        self.add_header(rows)
        for category in CATEGORY_ORDER:
            matching = [driver for driver in drivers if driver.category == category]
            if not matching:
                continue
            ctk.CTkLabel(
                rows,
                text=f"// {text(self.language, f'category_{category}')}",
                font=theme.font(17, "bold"),
                text_color=theme.TEXT,
            ).pack(anchor="w", pady=(10, 6))
            for driver in matching:
                self.add_driver_row(rows, driver)

    def add_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=(0, 12))
        set_columns(header)
        for column, key in enumerate(("column_device", "column_manufacturer", "column_date", "column_status")):
            ctk.CTkLabel(
                header,
                text=text(self.language, key).upper(),
                font=theme.font(15),
                text_color=theme.MUTED,
            ).grid(row=0, column=column, sticky="w", padx=(18, 0))

    def add_cell(self, card, column, main, detail, main_font, main_color, wrap):
        cell = ctk.CTkFrame(card, fg_color="transparent")
        cell.grid(row=0, column=column, sticky="w", padx=(18, 0), pady=12)
        ctk.CTkLabel(
            cell, text=main, font=main_font, text_color=main_color, wraplength=wrap, justify="left"
        ).pack(anchor="w")
        ctk.CTkLabel(
            cell, text=detail, font=theme.font(15), text_color=theme.MUTED, wraplength=wrap, justify="left"
        ).pack(anchor="w")

    def add_badge(self, card, status):
        color = theme.STATUS_COLORS[status]
        badge = ctk.CTkFrame(
            card,
            fg_color="transparent",
            border_color=color,
            border_width=1,
            corner_radius=theme.CORNER_RADIUS,
        )
        badge.grid(row=0, column=3, sticky="ew", padx=(18, 6))
        ctk.CTkLabel(
            badge,
            text=text(self.language, f"status_{status}").upper(),
            font=theme.font(16, "bold"),
            text_color=color,
            height=30,
        ).pack(padx=8, pady=2)

    def add_driver_row(self, parent, driver):
        language = self.language
        older = driver.status == OLDER
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.SURFACE,
            border_color=OLDER_ROW_BORDER if older else theme.BORDER,
            border_width=2,
            corner_radius=theme.CORNER_RADIUS,
        )
        card.pack(fill="x", pady=(0, 10), padx=(0, 12))
        set_columns(card)

        manufacturer = driver.manufacturer
        version = driver.version or text(language, "value_unknown")
        self.add_cell(
            card, 0, driver.name, f"{text(language, 'field_version')} {version}",
            theme.font(18, "bold"), theme.TEXT, NAME_WRAP,
        )
        self.add_cell(
            card, 1, manufacturer.name if manufacturer else driver.provider or text(language, "value_unknown"),
            "", theme.font(17), theme.MUTED, 100,
        )
        self.add_cell(
            card, 2, format_date(language, driver.driver_date), format_age(language, driver.age_months),
            theme.font(17), theme.MUTED, 170,
        )
        self.add_badge(card, driver.status)

        if manufacturer is None:
            ctk.CTkLabel(
                card,
                text=text(language, "check_manufacturer"),
                font=theme.font(15),
                text_color=theme.MUTED,
                wraplength=170,
                justify="left",
            ).grid(row=0, column=4, sticky="w", padx=14, pady=10)
            return
        make_button = theme.primary_button if older else theme.secondary_button
        open_button = make_button(
            card,
            text(language, "manufacturer_page"),
            lambda: self.open_page(manufacturer),
            height=42,
        )
        open_button.grid(row=0, column=4, sticky="ew", padx=14, pady=10)
        tkinter.Misc.bind(
            open_button,
            "<FocusIn>",
            lambda _event: theme.scroll_into_view(parent, card),
            add="+",
        )
        if manufacturer.pc_maker_note:
            ctk.CTkLabel(
                card,
                text=text(language, "pc_maker_note"),
                font=theme.font(15),
                text_color=theme.MUTED,
                wraplength=BODY_WRAP - 60,
                justify="left",
            ).grid(row=1, column=0, columnspan=5, sticky="w", padx=18, pady=(0, 10))

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

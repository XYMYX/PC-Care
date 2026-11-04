import customtkinter as ctk

from core.categories import BROWSER_NAMES
from core.cleanup import CLOSE_BROWSER, READY, total_freed, total_skipped
from core.settings import format_size
from core.texts import text
from ui import theme
from ui.background import run_in_background
from ui.dialogs import confirm

BODY_WRAP = 960
ROW_WRAP = 720
ADMIN_SURFACE = "#FCEBCF"
ADMIN_TEXT = "#7A4A00"


class CleanupScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.WHITE)
        self.app = app
        self.language = app.language
        self.previews = []
        self.choices = {}

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=40, pady=(30, 0))
        self.back_button = theme.secondary_button(top, text(self.language, "back"), app.show_start)
        self.back_button.pack(side="left")
        ctk.CTkLabel(
            top,
            text=text(self.language, "cleanup_title"),
            font=theme.font(28, "bold"),
            text_color=theme.TEXT,
        ).pack(side="left", padx=24)
        self.rescan_button = theme.secondary_button(top, text(self.language, "scan_rescan"), self.scan)
        self.rescan_button.pack(side="right")

        self.intro = ctk.CTkLabel(
            self,
            text=text(self.language, "cleanup_intro"),
            font=theme.font(18),
            text_color=theme.MUTED,
            wraplength=BODY_WRAP,
            justify="left",
        )
        self.intro.pack(anchor="w", padx=40, pady=(18, 12))

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=(40, 24))

        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=40, pady=(12, 24))
        self.scan()

    def clear(self, frame):
        for child in frame.winfo_children():
            child.destroy()

    def show_progress(self, message):
        self.clear(self.content)
        self.clear(self.footer)
        ctk.CTkLabel(
            self.content, text=message, font=theme.font(20), text_color=theme.TEXT
        ).pack(pady=(60, 16))
        self.progress = ctk.CTkProgressBar(
            self.content, mode="determinate", width=480, progress_color=theme.PRIMARY
        )
        self.progress.set(0)
        self.progress.pack()

    def update_progress(self, done, total):
        if total:
            self.progress.set(done / total)

    def set_buttons(self, enabled):
        state = "normal" if enabled else "disabled"
        self.back_button.configure(state=state)
        self.rescan_button.configure(state=state)
        self.app.busy = not enabled

    def scan(self):
        self.choices = {}
        self.intro.configure(text=text(self.language, "cleanup_intro"))
        self.show_progress(text(self.language, "scan_loading"))
        self.rescan_button.configure(state="disabled")
        cleaner = self.app.create_cleaner()
        self.cleaner = cleaner
        run_in_background(
            self, cleaner.preview, self.show_preview, self.show_scan_error, self.update_progress
        )

    def show_scan_error(self, _error):
        self.clear(self.content)
        self.rescan_button.configure(state="normal")
        ctk.CTkLabel(
            self.content,
            text=text(self.language, "scan_error"),
            font=theme.font(20),
            text_color=theme.TEXT,
        ).pack(pady=60)

    def show_preview(self, previews):
        self.previews = previews
        self.rescan_button.configure(state="normal")
        self.clear(self.content)
        rows = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        rows.pack(fill="both", expand=True)

        if self.app.same_user:
            self.add_heading(rows, "section_user")
            for preview in previews:
                if not preview.category.admin:
                    self.add_row(rows, preview)
        else:
            self.add_note(rows, "section_other_account")

        self.add_admin_banner(rows)
        for preview in previews:
            if preview.category.admin:
                self.add_row(rows, preview)
        self.build_footer()

    def add_heading(self, parent, key):
        ctk.CTkLabel(
            parent,
            text=text(self.language, key),
            font=theme.font(22, "bold"),
            text_color=theme.TEXT,
        ).pack(anchor="w", pady=(12, 8))

    def add_note(self, parent, key):
        ctk.CTkLabel(
            parent,
            text=text(self.language, key),
            font=theme.font(18),
            text_color=theme.TEXT,
            wraplength=BODY_WRAP,
            justify="left",
        ).pack(anchor="w", pady=(12, 8))

    def add_admin_banner(self, parent):
        banner = ctk.CTkFrame(parent, fg_color=ADMIN_SURFACE, corner_radius=12)
        banner.pack(fill="x", pady=(20, 10), padx=(0, 12))
        ctk.CTkLabel(
            banner,
            text=text(self.language, "section_admin"),
            font=theme.font(22, "bold"),
            text_color=ADMIN_TEXT,
        ).pack(anchor="w", padx=18, pady=(14, 2))
        hint_key = "section_admin_active" if self.app.is_admin else "section_admin_hint"
        ctk.CTkLabel(
            banner,
            text=text(self.language, hint_key),
            font=theme.font(17),
            text_color=ADMIN_TEXT,
            wraplength=BODY_WRAP - 60,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 14 if self.app.is_admin else 8))
        if self.app.is_admin:
            return
        theme.primary_button(
            banner, text(self.language, "admin_restart"), self.restart_as_admin
        ).pack(anchor="w", padx=18, pady=(0, 14))
        self.admin_message = ctk.CTkLabel(
            banner, text="", font=theme.font(17), text_color=ADMIN_TEXT
        )

    def status_text(self, status, category):
        if status == CLOSE_BROWSER:
            if category.process == "msedge":
                return text(self.language, "status_close_edge")
            return text(self.language, "status_close_browser", browser=BROWSER_NAMES[category.process])
        return text(self.language, f"status_{status}")

    def add_row(self, parent, preview):
        language = self.language
        category = preview.category
        available = preview.status == READY
        card = ctk.CTkFrame(
            parent, fg_color=theme.SURFACE, border_color=theme.BORDER, border_width=1, corner_radius=12
        )
        card.pack(fill="x", pady=(0, 10), padx=(0, 12))
        card.grid_columnconfigure(1, weight=1)

        choice = ctk.BooleanVar(value=False)
        box = ctk.CTkCheckBox(
            card,
            text="",
            variable=choice,
            command=self.update_selection,
            state="normal" if available else "disabled",
            width=32,
            checkbox_width=32,
            checkbox_height=32,
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            border_color=theme.MUTED if available else theme.BORDER,
        )
        box.grid(row=0, column=0, rowspan=2, padx=(18, 8), pady=14)
        if available:
            self.choices[category.key] = choice

        name_color = theme.TEXT if available else theme.DISABLED_TEXT
        ctk.CTkLabel(
            card,
            text=text(language, f"cat_{category.key}"),
            font=theme.font(19, "bold"),
            text_color=name_color,
        ).grid(row=0, column=1, sticky="w", pady=(12, 0))
        details = text(language, f"cat_{category.key}_hint")
        if not available:
            details = f"{self.status_text(preview.status, category)}\n{details}"
        ctk.CTkLabel(
            card,
            text=details,
            font=theme.font(16),
            text_color=theme.TEXT if preview.status == CLOSE_BROWSER else theme.MUTED,
            wraplength=ROW_WRAP,
            justify="left",
        ).grid(row=1, column=1, sticky="w", pady=(0, 12))
        if preview.size:
            ctk.CTkLabel(
                card,
                text=format_size(preview.size, language),
                font=theme.font(19, "bold"),
                text_color=name_color,
            ).grid(row=0, column=2, rowspan=2, padx=18)

    def build_footer(self):
        self.clear(self.footer)
        self.selection_label = ctk.CTkLabel(
            self.footer, text="", font=theme.font(20, "bold"), text_color=theme.TEXT
        )
        self.selection_label.pack(side="left")
        self.clean_button = theme.primary_button(
            self.footer, text(self.language, "clean_button"), self.confirm_clean
        )
        self.clean_button.pack(side="right")
        self.update_selection()

    def selected_previews(self):
        return [
            preview
            for preview in self.previews
            if preview.category.key in self.choices and self.choices[preview.category.key].get()
        ]

    def update_selection(self):
        selected = self.selected_previews()
        total = sum(preview.size for preview in selected)
        self.selection_label.configure(
            text=text(self.language, "selected_total", size=format_size(total, self.language))
        )
        self.clean_button.configure(
            state="normal" if selected else "disabled",
            fg_color=theme.PRIMARY if selected else theme.BORDER,
            text_color_disabled=theme.DISABLED_TEXT,
        )

    def restart_as_admin(self):
        confirmed = confirm(
            self.app,
            text(self.language, "admin_restart_title"),
            text(self.language, "admin_restart_body"),
            text(self.language, "admin_restart_confirm"),
            text(self.language, "cancel"),
        )
        if confirmed and not self.app.restart_as_admin():
            self.admin_message.configure(text=text(self.language, "admin_restart_cancelled"))
            self.admin_message.pack(anchor="w", padx=18, pady=(0, 14))

    def confirm_clean(self):
        selected = self.selected_previews()
        names = "\n".join(f"• {text(self.language, f'cat_{preview.category.key}')}" for preview in selected)
        size = format_size(sum(preview.size for preview in selected), self.language)
        confirmed = confirm(
            self.app,
            text(self.language, "confirm_clean_title"),
            text(self.language, "confirm_clean_body", names=names, size=size),
            text(self.language, "confirm_clean_action"),
            text(self.language, "cancel"),
        )
        if confirmed:
            self.start_clean([preview.category.key for preview in selected])

    def start_clean(self, keys):
        self.show_progress(text(self.language, "cleaning"))
        self.set_buttons(False)
        run_in_background(
            self,
            lambda report: self.cleaner.clean(keys, report),
            self.show_result,
            self.show_clean_error,
            self.update_progress,
        )

    def show_clean_error(self, _error):
        self.set_buttons(True)
        self.show_scan_error(_error)

    def show_result(self, outcomes):
        self.set_buttons(True)
        self.app.add_freed_space(total_freed(outcomes))
        self.intro.configure(text=text(self.language, "result_title"))
        self.clear(self.content)
        self.clear(self.footer)
        language = self.language
        ctk.CTkLabel(
            self.content,
            text=text(language, "result_freed", size=format_size(total_freed(outcomes), language)),
            font=theme.font(30, "bold"),
            text_color=theme.TEXT,
        ).pack(anchor="w", pady=(24, 12))
        skipped = total_skipped(outcomes)
        ctk.CTkLabel(
            self.content,
            text=text(language, "result_skipped", count=skipped),
            font=theme.font(20),
            text_color=theme.TEXT,
        ).pack(anchor="w")
        if skipped:
            ctk.CTkLabel(
                self.content,
                text=text(language, "result_skipped_hint"),
                font=theme.font(17),
                text_color=theme.MUTED,
            ).pack(anchor="w")
        not_cleaned = [outcome for outcome in outcomes if outcome.status != READY]
        if not_cleaned:
            ctk.CTkLabel(
                self.content,
                text=text(language, "result_not_cleaned"),
                font=theme.font(20, "bold"),
                text_color=theme.TEXT,
            ).pack(anchor="w", pady=(24, 4))
        for outcome in not_cleaned:
            reason = self.status_text(outcome.status, outcome.category)
            ctk.CTkLabel(
                self.content,
                text=f"{text(language, f'cat_{outcome.category.key}')}: {reason}",
                font=theme.font(17),
                text_color=theme.TEXT,
                wraplength=BODY_WRAP,
                justify="left",
            ).pack(anchor="w")
        theme.primary_button(self.footer, text(language, "result_back"), self.scan).pack(side="right")

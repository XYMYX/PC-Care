import sys

import customtkinter as ctk

from core import admin
from core.categories import build_categories, runtime_exclusions, system_paths
from core.cleanup import Cleaner
from core.settings import add_freed, app_data_dir, load_settings, save_settings
from core.texts import text
from ui import theme
from ui.cleanup_screen import CleanupScreen
from ui.driver_screen import DriverScreen
from ui.start_screen import StartScreen


class App(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("light")
        super().__init__(fg_color=theme.WHITE)
        options = admin.parse_options(sys.argv[1:])
        self.is_admin = admin.is_admin()
        self.settings_folder = (options.settings_folder if self.is_admin else None) or app_data_dir()
        self.original_user = (options.original_user if self.is_admin else None) or admin.current_user()
        self.same_user = self.original_user == admin.current_user()
        self.settings = load_settings(self.settings_folder)
        self.busy = False
        self.title(text(self.language, "app_title"))
        self.geometry(theme.WINDOW_SIZE)
        self.minsize(theme.MIN_WIDTH, theme.MIN_HEIGHT)
        self.protocol("WM_DELETE_WINDOW", self.request_close)
        self.screen = None
        self.show_start()

    @property
    def language(self):
        return self.settings["language"]

    def request_close(self):
        if not self.busy:
            self.destroy()

    def set_language(self, language):
        self.settings["language"] = language
        save_settings(self.settings, self.settings_folder)
        self.title(text(language, "app_title"))
        self.show_start()

    def add_freed_space(self, freed_bytes):
        add_freed(self.settings, freed_bytes, self.settings_folder)

    def create_cleaner(self):
        categories = build_categories(system_paths(), runtime_exclusions())
        return Cleaner(categories, self.is_admin, self.same_user, log_folder=self.settings_folder)

    def restart_as_admin(self):
        if admin.restart_as_admin(self.settings_folder, self.original_user):
            self.destroy()
            return True
        return False

    def show_screen(self, screen_class):
        if self.screen is not None:
            self.screen.destroy()
        self.screen = screen_class(self, self)
        self.screen.pack(fill="both", expand=True)
        self.focus_set()

    def show_start(self):
        self.show_screen(StartScreen)

    def show_drivers(self):
        self.show_screen(DriverScreen)

    def show_cleanup(self):
        self.show_screen(CleanupScreen)

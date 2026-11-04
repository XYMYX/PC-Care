import customtkinter as ctk

from core.settings import format_size
from core.texts import LANGUAGES, text
from ui import theme


class StartScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.WHITE)
        self.app = app
        language = app.language

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=40, pady=(30, 0))
        ctk.CTkLabel(
            top, text="XYMYX", font=theme.font(32, "bold"), text_color=theme.BLACK
        ).pack(side="left")
        for code, name in reversed(LANGUAGES.items()):
            make_button = theme.primary_button if code == language else theme.secondary_button
            make_button(top, name, lambda selected=code: app.set_language(selected), width=120).pack(
                side="right", padx=(8, 0)
            )

        ctk.CTkLabel(
            self,
            text=text(language, "start_intro"),
            font=theme.font(22),
            text_color=theme.TEXT,
        ).pack(anchor="w", padx=40, pady=(40, 24))

        tiles = ctk.CTkFrame(self, fg_color="transparent")
        tiles.pack(fill="both", expand=True, padx=40)
        tiles.grid_columnconfigure((0, 1), weight=1, uniform="tile")
        tiles.grid_rowconfigure(0, weight=1)
        self.add_tile(tiles, 0, "tile_drivers", "tile_drivers_hint", app.show_drivers)
        self.add_tile(tiles, 1, "tile_cleanup", "tile_cleanup_hint", app.show_cleanup)

        ctk.CTkLabel(
            self,
            text=text(language, "freed_total", size=format_size(app.settings["freed_bytes_total"], language)),
            font=theme.font(22, "bold"),
            text_color=theme.TEXT,
        ).pack(anchor="w", padx=40, pady=30)

    def add_tile(self, parent, column, title_key, hint_key, command):
        language = self.app.language
        title_color = theme.TEXT if command else theme.DISABLED_TEXT
        hint_color = theme.MUTED if command else theme.DISABLED_TEXT
        tile = ctk.CTkFrame(
            parent, fg_color=theme.SURFACE, border_color=theme.BORDER, border_width=2, corner_radius=16
        )
        tile.grid(row=0, column=column, sticky="nsew", padx=(0, 12) if column == 0 else (12, 0))
        tile.grid_columnconfigure(0, weight=1)
        tile.grid_rowconfigure((0, 3), weight=1)
        title = ctk.CTkLabel(
            tile, text=text(language, title_key), font=theme.font(32, "bold"), text_color=title_color
        )
        title.grid(row=1, column=0, padx=24, pady=(0, 10))
        hint = ctk.CTkLabel(
            tile,
            text=text(language, hint_key),
            font=theme.font(19),
            text_color=hint_color,
            wraplength=360,
        )
        hint.grid(row=2, column=0, padx=24)
        if command is None:
            return
        for area in (tile, title, hint):
            area.configure(cursor="hand2")
            area.bind("<Button-1>", lambda _event: command())
            area.bind("<Enter>", lambda _event: tile.configure(fg_color=theme.SECONDARY_HOVER))
            area.bind("<Leave>", lambda _event: tile.configure(fg_color=theme.SURFACE))

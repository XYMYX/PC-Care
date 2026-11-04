import tkinter

import customtkinter as ctk

from core.settings import format_size
from core.texts import LANGUAGES, text
from ui import logo, theme
from ui.matrix_rain import MatrixRain

SYMBOL_DRAW_HEIGHT = 62
SYMBOL_TOP = 22
TILE_LEFT = 40 / 1100
TILE_TOP = 170 / 780
TILE_WIDTH = 498 / 1100
TILE_HEIGHT = 390 / 780
TILE_GAP = 24 / 1100
FOOTER_TOP = 602 / 780


class StartScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.BACKGROUND)
        self.app = app
        self.language = app.language

        self.canvas = MatrixRain(self)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.canvas.bind("<Configure>", self.draw_text, add="+")

        codes = list(LANGUAGES.items())
        for position, (code, name) in enumerate(codes):
            make_button = theme.primary_button if code == self.language else theme.secondary_button
            button = make_button(self, name, lambda selected=code: app.set_language(selected), width=115)
            button.place(relx=1.0, x=-40 - 125 * (len(codes) - 1 - position), y=30, anchor="ne")

        self.add_tile(0, "[01]", "tile_drivers", "tile_drivers_hint", app.show_drivers, self.draw_table_icon)
        self.add_tile(1, "[02]", "tile_cleanup", "tile_cleanup_hint", app.show_cleanup, self.draw_box_icon)

    def scaled(self, value):
        return round(value * ctk.ScalingTracker.get_widget_scaling(self))

    def draw_symbol(self, x, y):
        height = self.scaled(SYMBOL_DRAW_HEIGHT)
        scale = height / logo.SYMBOL_HEIGHT
        width = round(logo.SYMBOL_WIDTH * scale)
        stroke = max(2, round(logo.STROKE_WIDTH * scale))
        margin = self.scaled(6)
        self.canvas.create_rectangle(
            x - margin, y - margin, x + width + margin, y + height + margin,
            fill=theme.BACKGROUND, width=0, tags="ui",
        )
        for (start_x, start_y), (end_x, end_y) in logo.STROKES:
            self.canvas.create_line(
                x + start_x * scale, y + start_y * scale, x + end_x * scale, y + end_y * scale,
                fill=theme.TEXT, width=stroke, capstyle="round", tags="ui",
            )
        return x + width

    def draw_product_name(self, x, y):
        step = self.scaled(16)
        label_font = theme.canvas_font(self, 21, "bold")
        for character in "PC//CARE":
            color = theme.DISABLED_TEXT if character == "/" else theme.TEXT
            self.canvas.create_text(x, y, text=character, font=label_font, fill=color, anchor="w", tags="ui")
            x += step

    def draw_label(self, x, y, label, anchor, label_font):
        item = self.canvas.create_text(
            x, y, text=label, font=label_font, fill=theme.TEXT, anchor=anchor, tags="ui"
        )
        left, top, right, bottom = self.canvas.bbox(item)
        margin = self.scaled(6)
        self.canvas.create_rectangle(
            left - margin, top - margin, right + margin, bottom + margin,
            fill=theme.BACKGROUND, width=0, tags="ui",
        )
        self.canvas.tag_raise(item)

    def draw_text(self, event):
        self.canvas.delete("ui")
        language = self.language
        left = self.scaled(40)
        symbol_end = self.draw_symbol(left, self.scaled(SYMBOL_TOP))
        self.draw_product_name(symbol_end + self.scaled(20), self.scaled(SYMBOL_TOP + SYMBOL_DRAW_HEIGHT / 2))
        self.draw_label(
            left, self.scaled(132), f"> {text(language, 'start_intro')}", "w",
            theme.canvas_font(self, 21),
        )
        footer_y = round(event.height * FOOTER_TOP)
        size = format_size(self.app.settings["freed_bytes_total"], language)
        self.draw_label(
            left, footer_y, text(language, "freed_total", size=size), "w",
            theme.canvas_font(self, 21, "bold"),
        )

    def add_tile(self, column, tag, title_key, hint_key, command, draw_icon):
        tile = ctk.CTkFrame(
            self,
            fg_color=theme.SURFACE,
            border_color=theme.BORDER,
            border_width=2,
            corner_radius=theme.CORNER_RADIUS,
        )
        tile.place(
            relx=TILE_LEFT + column * (TILE_WIDTH + TILE_GAP),
            rely=TILE_TOP,
            relwidth=TILE_WIDTH,
            relheight=TILE_HEIGHT,
        )
        tile.grid_columnconfigure(0, weight=1)
        tile.grid_rowconfigure((0, 4), weight=1)
        badge = ctk.CTkLabel(tile, text=tag, font=theme.font(15), text_color=theme.DISABLED_TEXT)
        badge.place(x=18, y=10)
        icon = tkinter.Canvas(
            tile,
            width=self.scaled(64),
            height=self.scaled(44),
            bg=theme.SURFACE,
            highlightthickness=0,
            takefocus=0,
        )
        icon.grid(row=1, column=0, pady=(0, 14))
        draw_icon(icon)
        title = ctk.CTkLabel(
            tile,
            text=text(self.language, title_key).upper(),
            font=theme.font(34, "bold"),
            text_color=theme.TEXT,
        )
        title.grid(row=2, column=0, padx=20, pady=(0, 10))
        hint = ctk.CTkLabel(
            tile,
            text=text(self.language, hint_key),
            font=theme.font(19),
            text_color=theme.MUTED,
            wraplength=430,
        )
        hint.grid(row=3, column=0, padx=20)

        theme.enable_keyboard(tile, command)

        def hover(color):
            if tile.focus_get() is not tile:
                tile.configure(border_color=color)

        tkinter.Misc.configure(icon, cursor="hand2")
        for area in (tile, badge, icon, title, hint):
            if area is not icon:
                area.configure(cursor="hand2")
            area.bind("<Button-1>", lambda _event: command())
            area.bind("<Enter>", lambda _event: hover(theme.TEXT))
            area.bind("<Leave>", lambda _event: hover(theme.BORDER))

    def draw_table_icon(self, icon):
        width, height = self.scaled(60), self.scaled(32)
        left, top = self.scaled(2), self.scaled(6)
        icon.create_rectangle(left, top, left + width, top + height, outline=theme.TEXT)
        for column in (1, 2):
            x = left + width * column // 3
            icon.create_line(x, top, x, top + height, fill=theme.TEXT)
        middle = top + height // 2
        icon.create_line(left, middle, left + width, middle, fill=theme.TEXT)

    def draw_box_icon(self, icon):
        wall = self.scaled(10)
        width, height = self.scaled(60), self.scaled(40)
        left, top = self.scaled(2), self.scaled(2)
        icon.create_rectangle(left, top, left + width, top + height, fill=theme.MUTED, width=0)
        icon.create_rectangle(
            left + wall, top + wall, left + width - wall, top + height - wall,
            fill=theme.BLACK, width=0,
        )
        icon.create_rectangle(
            left + wall, top + wall, left + width - wall, top + height - wall,
            fill=theme.MUTED, stipple="gray50", width=0,
        )

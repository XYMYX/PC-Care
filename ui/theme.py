import customtkinter as ctk

WHITE = "#FFFFFF"
BLACK = "#000000"
TEXT = "#1A1A1A"
MUTED = "#5A5A5A"
SURFACE = "#F3F4F6"
BORDER = "#D9DBE0"
PRIMARY = "#1A1A1A"
PRIMARY_HOVER = "#3A3A3A"
SECONDARY_HOVER = "#E5E7EB"
DISABLED_TEXT = "#6B6B6B"

STATUS_COLORS = {
    "recent": ("#DDF3E4", "#14592D"),
    "older": ("#FCEBCF", "#7A4A00"),
    "unknown": ("#E5E7EB", "#3A3A3A"),
}

FONT_FAMILY = "Segoe UI"
WINDOW_SIZE = "1100x780"
MIN_WIDTH = 900
MIN_HEIGHT = 640


def font(size=18, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def primary_button(parent, label, command, **options):
    return ctk.CTkButton(
        parent,
        text=label,
        command=command,
        font=font(18, "bold"),
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color=WHITE,
        height=52,
        corner_radius=10,
        **options,
    )


def secondary_button(parent, label, command, **options):
    return ctk.CTkButton(
        parent,
        text=label,
        command=command,
        font=font(18),
        fg_color=WHITE,
        hover_color=SECONDARY_HOVER,
        text_color=TEXT,
        border_color=BORDER,
        border_width=2,
        height=52,
        corner_radius=10,
        **options,
    )

import tkinter

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
FOCUS_RING = "#2563EB"

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


def enable_keyboard(widget, activate, ring=None, on_focus=None):
    outlined = ring or widget
    resting_color = {}

    def press(_event):
        activate()
        return "break"

    def show_ring(_event):
        resting_color["value"] = outlined.cget("border_color")
        outlined.configure(border_color=FOCUS_RING)
        if on_focus:
            on_focus()

    def hide_ring(_event):
        outlined.configure(border_color=resting_color.get("value", BORDER))

    tkinter.Frame.configure(widget, takefocus=True)
    tkinter.Misc.bind(widget, "<Return>", press)
    tkinter.Misc.bind(widget, "<space>", press)
    tkinter.Misc.bind(widget, "<FocusIn>", show_ring)
    tkinter.Misc.bind(widget, "<FocusOut>", hide_ring)


def scroll_into_view(scrollable, widget):
    canvas = scrollable._parent_canvas
    canvas.update_idletasks()
    total = scrollable.winfo_height()
    visible = canvas.winfo_height()
    top = widget.winfo_rooty() - scrollable.winfo_rooty()
    bottom = top + widget.winfo_height()
    view_top = canvas.yview()[0] * total
    if top < view_top:
        canvas.yview_moveto(top / total)
    elif bottom > view_top + visible:
        canvas.yview_moveto((bottom - visible) / total)


def primary_button(parent, label, command, **options):
    button = ctk.CTkButton(
        parent,
        text=label,
        command=command,
        font=font(18, "bold"),
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color=WHITE,
        border_color=PRIMARY,
        border_width=3,
        height=52,
        corner_radius=10,
        **options,
    )
    enable_keyboard(button, button.invoke)
    return button


def secondary_button(parent, label, command, **options):
    button = ctk.CTkButton(
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
    enable_keyboard(button, button.invoke)
    return button

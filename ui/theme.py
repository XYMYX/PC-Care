import tkinter

import customtkinter as ctk

BACKGROUND = "#000000"
BLACK = "#000000"
TEXT = "#FFFFFF"
MUTED = "#A8A8A8"
SURFACE = "#0B0B0B"
BORDER = "#3A3A3A"
PRIMARY = "#FFFFFF"
PRIMARY_HOVER = "#D4D4D4"
SECONDARY_HOVER = "#1E1E1E"
DISABLED_TEXT = "#858585"
DISABLED_FILL = "#1A1A1A"
AMBER = "#FFC857"
FOCUS_RING = AMBER

STATUS_COLORS = {
    "recent": TEXT,
    "older": AMBER,
    "unknown": MUTED,
}

FONT_FAMILY = "Consolas"
CORNER_RADIUS = 4
WINDOW_SIZE = "1100x780"
MIN_WIDTH = 900
MIN_HEIGHT = 640


def font(size=18, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def canvas_font(widget, size, weight="normal"):
    pixels = round(size * ctk.ScalingTracker.get_widget_scaling(widget))
    return (FONT_FAMILY, -pixels, weight)


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
        font=font(17, "bold"),
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color=BLACK,
        border_color=PRIMARY,
        border_width=2,
        border_spacing=8,
        height=options.pop("height", 48),
        corner_radius=CORNER_RADIUS,
        **options,
    )
    enable_keyboard(button, button.invoke)
    return button


def secondary_button(parent, label, command, **options):
    button = ctk.CTkButton(
        parent,
        text=label,
        command=command,
        font=font(17),
        fg_color=BACKGROUND,
        hover_color=SECONDARY_HOVER,
        text_color=TEXT,
        border_color=BORDER,
        border_width=2,
        border_spacing=8,
        height=options.pop("height", 48),
        corner_radius=CORNER_RADIUS,
        **options,
    )
    enable_keyboard(button, button.invoke)
    return button


def title_label(parent, label):
    return ctk.CTkLabel(parent, text=label.upper(), font=font(30, "bold"), text_color=TEXT)


def scrollable_frame(parent):
    return ctk.CTkScrollableFrame(
        parent,
        fg_color="transparent",
        scrollbar_button_color=BORDER,
        scrollbar_button_hover_color=MUTED,
    )


def progress_bar(parent, mode):
    return ctk.CTkProgressBar(
        parent,
        mode=mode,
        width=480,
        height=14,
        corner_radius=0,
        fg_color=DISABLED_FILL,
        progress_color=PRIMARY,
    )

import customtkinter as ctk

from ui import theme

DIALOG_WIDTH = 620
TEXT_WRAP = 560


def confirm(parent, title, message, confirm_label, cancel_label):
    answer = {"confirmed": False}
    dialog = ctk.CTkToplevel(parent, fg_color=theme.WHITE)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.transient(parent)

    def choose(confirmed):
        answer["confirmed"] = confirmed
        dialog.grab_release()
        dialog.destroy()

    ctk.CTkLabel(
        dialog,
        text=title,
        font=theme.font(24, "bold"),
        text_color=theme.TEXT,
        wraplength=TEXT_WRAP,
        justify="left",
    ).pack(anchor="w", padx=30, pady=(28, 10))
    ctk.CTkLabel(
        dialog,
        text=message,
        font=theme.font(18),
        text_color=theme.TEXT,
        wraplength=TEXT_WRAP,
        justify="left",
    ).pack(anchor="w", padx=30)

    buttons = ctk.CTkFrame(dialog, fg_color="transparent")
    buttons.pack(fill="x", padx=30, pady=28)
    theme.primary_button(buttons, confirm_label, lambda: choose(True)).pack(side="right")
    theme.secondary_button(buttons, cancel_label, lambda: choose(False)).pack(side="right", padx=(0, 12))

    dialog.protocol("WM_DELETE_WINDOW", lambda: choose(False))
    dialog.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - DIALOG_WIDTH) // 2
    y = parent.winfo_rooty() + 120
    dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    dialog.after(50, dialog.grab_set)
    dialog.wait_window()
    return answer["confirmed"]

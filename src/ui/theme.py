"""
Theme manager and ttk styles for Modern Dark & Light modes.
"""
from tkinter import ttk
import tkinter as tk

THEMES = {
    "dark": {
        "bg": "#181825",
        "card_bg": "#1e1e2e",
        "surface": "#24273a",
        "border": "#313244",
        "fg": "#cdd6f4",
        "muted": "#a6adc8",
        "primary": "#0066FF",
        "primary_hover": "#0052CC",
        "primary_fg": "#ffffff",
        "danger": "#e63946",
        "danger_hover": "#c82333",
        "danger_fg": "#ffffff",
        "success": "#2ec4b6",
        "warning": "#ff9f1c",
        "entry_bg": "#24273a",
        "entry_fg": "#cdd6f4",
        "select_bg": "#313244",
        "progress_trough": "#24273a",
    },
    "light": {
        "bg": "#f4f6f9",
        "card_bg": "#ffffff",
        "surface": "#e9ecef",
        "border": "#dee2e6",
        "fg": "#1a1a2e",
        "muted": "#6c757d",
        "primary": "#004ECA",
        "primary_hover": "#003bb5",
        "primary_fg": "#ffffff",
        "danger": "#dc3545",
        "danger_hover": "#bd2130",
        "danger_fg": "#ffffff",
        "success": "#198754",
        "warning": "#fd7e14",
        "entry_bg": "#ffffff",
        "entry_fg": "#1a1a2e",
        "select_bg": "#004ECA",
        "progress_trough": "#e9ecef",
    }
}

current_theme = "dark"


def get_current_theme():
    return current_theme


def get_theme_colors(theme_name=None):
    t = theme_name or current_theme
    return THEMES.get(t, THEMES["dark"])


def apply_theme(root: tk.Tk, theme_name: str = "dark"):
    """Configures the ttk styles and root colors for the chosen theme."""
    global current_theme
    if theme_name not in THEMES:
        theme_name = "dark"
    current_theme = theme_name

    c = THEMES[theme_name]
    root.configure(bg=c["bg"])

    style = ttk.Style(root)
    # Use 'clam' as base engine for predictable color customizations
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Root Frames
    style.configure("TFrame", background=c["bg"])
    style.configure("Card.TFrame", background=c["card_bg"], relief="flat")
    style.configure("Surface.TFrame", background=c["surface"], relief="flat")

    # Labels
    style.configure("TLabel", background=c["bg"], foreground=c["fg"], font=("Segoe UI", 10))
    style.configure("Card.TLabel", background=c["card_bg"], foreground=c["fg"], font=("Segoe UI", 10))
    style.configure("Title.TLabel", background=c["bg"], foreground=c["fg"], font=("Segoe UI", 14, "bold"))
    style.configure("CardTitle.TLabel", background=c["card_bg"], foreground=c["fg"], font=("Segoe UI", 11, "bold"))
    style.configure("Muted.TLabel", background=c["card_bg"], foreground=c["muted"], font=("Segoe UI", 9))
    style.configure("MutedRoot.TLabel", background=c["bg"], foreground=c["muted"], font=("Segoe UI", 9))
    style.configure("Badge.TLabel", background=c["surface"], foreground=c["primary"], font=("Segoe UI", 9, "bold"))

    # Buttons
    style.configure(
        "TButton",
        background=c["surface"],
        foreground=c["fg"],
        borderwidth=0,
        focuscolor="none",
        font=("Segoe UI", 10),
        padding=6
    )
    style.map(
        "TButton",
        background=[("active", c["border"]), ("disabled", c["surface"])],
        foreground=[("disabled", c["muted"])]
    )

    style.configure(
        "Primary.TButton",
        background=c["primary"],
        foreground=c["primary_fg"],
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
        focuscolor="none",
        padding=(12, 6)
    )
    style.map(
        "Primary.TButton",
        background=[("active", c["primary_hover"]), ("disabled", c["surface"])],
        foreground=[("disabled", c["muted"])]
    )

    style.configure(
        "Danger.TButton",
        background=c["danger"],
        foreground=c["danger_fg"],
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
        focuscolor="none",
        padding=(10, 6)
    )
    style.map(
        "Danger.TButton",
        background=[("active", c["danger_hover"]), ("disabled", c["surface"])],
        foreground=[("disabled", c["muted"])]
    )

    # Entry
    style.configure(
        "TEntry",
        fieldbackground=c["entry_bg"],
        foreground=c["entry_fg"],
        insertcolor=c["fg"],
        bordercolor=c["border"],
        lightcolor=c["border"],
        darkcolor=c["border"],
        padding=6
    )

    # Combobox
    style.configure(
        "TCombobox",
        fieldbackground=c["entry_bg"],
        background=c["surface"],
        foreground=c["entry_fg"],
        arrowcolor=c["fg"],
        bordercolor=c["border"],
        lightcolor=c["border"],
        darkcolor=c["border"],
        padding=4
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", c["entry_bg"])],
        foreground=[("readonly", c["entry_fg"])],
        selectbackground=[("readonly", c["select_bg"])],
        selectforeground=[("readonly", c["fg"])],
    )

    # Progressbar
    style.configure(
        "Horizontal.TProgressbar",
        troughcolor=c["progress_trough"],
        background=c["primary"],
        bordercolor=c["border"],
        lightcolor=c["primary"],
        darkcolor=c["primary"],
        thickness=10
    )

    # Treeview (for history and queue tables)
    style.configure(
        "Treeview",
        background=c["card_bg"],
        foreground=c["fg"],
        fieldbackground=c["card_bg"],
        bordercolor=c["border"],
        rowheight=26,
        font=("Segoe UI", 9)
    )
    style.configure(
        "Treeview.Heading",
        background=c["surface"],
        foreground=c["fg"],
        relief="flat",
        font=("Segoe UI", 9, "bold"),
        padding=4
    )
    style.map(
        "Treeview",
        background=[("selected", c["primary"])],
        foreground=[("selected", c["primary_fg"])]
    )
    style.map(
        "Treeview.Heading",
        background=[("active", c["border"])]
    )

    # Radiobuttons
    style.configure(
        "TRadiobutton",
        background=c["card_bg"],
        foreground=c["fg"],
        focuscolor="none",
        font=("Segoe UI", 9)
    )
    style.map(
        "TRadiobutton",
        background=[("active", c["card_bg"])],
        foreground=[("active", c["primary"])]
    )

    # Notebook (Tabs)
    style.configure(
        "TNotebook",
        background=c["bg"],
        tabmargins=[2, 5, 2, 0],
        borderwidth=0
    )
    style.configure(
        "TNotebook.Tab",
        background=c["surface"],
        foreground=c["muted"],
        padding=[14, 6],
        font=("Segoe UI", 10, "bold"),
        borderwidth=0
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", c["card_bg"])],
        foreground=[("selected", c["primary"])],
        expand=[("selected", [0, 2, 0, 0])]
    )

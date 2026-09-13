"""
Settings and Preferences dialog.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional

from ...config import (
    config,
    VIDEO_QUALITIES,
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    AUDIO_BITRATES
)
from ...core.utils import detect_ffmpeg
from ..theme import get_theme_colors, apply_theme


class SettingsDialog(tk.Toplevel):
    """Modal dialog for configuring application preferences."""

    def __init__(self, parent, on_save_callback: Optional[Callable] = None):
        super().__init__(parent)
        self.title("Settings & Preferences")
        self.geometry("560x520")
        self.resizable(False, False)
        self.transient(parent)

        self.on_save_callback = on_save_callback
        self._build_ui()

    def _build_ui(self):
        c = get_theme_colors()
        self.configure(bg=c["bg"])

        main_frame = tk.Frame(self, bg=c["bg"], padx=20, pady=16)
        main_frame.pack(fill="both", expand=True)

        # 1. Download Path Section
        lbl_sec1 = tk.Label(main_frame, text="📁 Download Location", font=("Segoe UI", 10, "bold"), fg=c["fg"], bg=c["bg"])
        lbl_sec1.pack(anchor="w", pady=(0, 4))

        path_row = tk.Frame(main_frame, bg=c["bg"])
        path_row.pack(fill="x", pady=(0, 14))

        self.path_var = tk.StringVar(value=config.get("download_dir"))
        self.path_entry = ttk.Entry(path_row, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse = ttk.Button(path_row, text="Browse...", style="TButton", command=self._browse_dir)
        btn_browse.pack(side="right")

        # 2. Appearance Section
        lbl_sec2 = tk.Label(main_frame, text="🎨 Appearance & Notifications", font=("Segoe UI", 10, "bold"), fg=c["fg"], bg=c["bg"])
        lbl_sec2.pack(anchor="w", pady=(0, 4))

        theme_row = tk.Frame(main_frame, bg=c["bg"])
        theme_row.pack(fill="x", pady=(0, 10))

        tk.Label(theme_row, text="Theme:", font=("Segoe UI", 9), fg=c["fg"], bg=c["bg"]).pack(side="left", padx=(0, 10))
        self.theme_var = tk.StringVar(value=config.get("theme", "dark"))
        self.theme_combo = ttk.Combobox(theme_row, textvariable=self.theme_var, values=["dark", "light"], state="readonly", width=12)
        self.theme_combo.pack(side="left", padx=(0, 20))

        self.notif_var = tk.BooleanVar(value=config.get("notifications_enabled", True))
        self.notif_check = ttk.Checkbutton(theme_row, text="Enable Desktop Notifications", variable=self.notif_var)
        self.notif_check.pack(side="left")

        # 3. Default Download Presets
        lbl_sec3 = tk.Label(main_frame, text="⚙️ Default Presets", font=("Segoe UI", 10, "bold"), fg=c["fg"], bg=c["bg"])
        lbl_sec3.pack(anchor="w", pady=(0, 4))

        presets_frame = ttk.Frame(main_frame, style="Card.TFrame")
        presets_frame.pack(fill="x", pady=(0, 14))

        preset_inner = tk.Frame(presets_frame, bg=c["card_bg"], padx=12, pady=10)
        preset_inner.pack(fill="x")

        # Video quality & format
        row1 = tk.Frame(preset_inner, bg=c["card_bg"])
        row1.pack(fill="x", pady=2)
        tk.Label(row1, text="Default Video Quality:", font=("Segoe UI", 9), fg=c["fg"], bg=c["card_bg"], width=20, anchor="w").pack(side="left")
        self.vquality_var = tk.StringVar(value=config.get("default_video_quality", "best"))
        ttk.Combobox(row1, textvariable=self.vquality_var, values=VIDEO_QUALITIES, state="readonly", width=12).pack(side="left", padx=(0, 15))

        tk.Label(row1, text="Video Format:", font=("Segoe UI", 9), fg=c["fg"], bg=c["card_bg"]).pack(side="left", padx=(0, 6))
        self.vformat_var = tk.StringVar(value=config.get("default_video_format", "mp4"))
        ttk.Combobox(row1, textvariable=self.vformat_var, values=VIDEO_FORMATS, state="readonly", width=8).pack(side="left")

        # Audio quality & bitrate
        row2 = tk.Frame(preset_inner, bg=c["card_bg"])
        row2.pack(fill="x", pady=4)
        tk.Label(row2, text="Default Audio Bitrate:", font=("Segoe UI", 9), fg=c["fg"], bg=c["card_bg"], width=20, anchor="w").pack(side="left")
        self.abitrate_var = tk.StringVar(value=config.get("default_audio_bitrate", "192"))
        ttk.Combobox(row2, textvariable=self.abitrate_var, values=AUDIO_BITRATES, state="readonly", width=12).pack(side="left", padx=(0, 15))

        tk.Label(row2, text="Audio Format:", font=("Segoe UI", 9), fg=c["fg"], bg=c["card_bg"]).pack(side="left", padx=(0, 6))
        self.aformat_var = tk.StringVar(value=config.get("default_audio_format", "mp3"))
        ttk.Combobox(row2, textvariable=self.aformat_var, values=AUDIO_FORMATS, state="readonly", width=8).pack(side="left")

        # 4. FFmpeg Section
        lbl_sec4 = tk.Label(main_frame, text="🎞️ FFmpeg Location", font=("Segoe UI", 10, "bold"), fg=c["fg"], bg=c["bg"])
        lbl_sec4.pack(anchor="w", pady=(0, 4))

        ffmpeg_row = tk.Frame(main_frame, bg=c["bg"])
        ffmpeg_row.pack(fill="x", pady=(0, 4))

        self.ffmpeg_var = tk.StringVar(value=config.get("custom_ffmpeg_path", ""))
        self.ffmpeg_entry = ttk.Entry(ffmpeg_row, textvariable=self.ffmpeg_var)
        self.ffmpeg_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse_ff = ttk.Button(ffmpeg_row, text="Browse...", style="TButton", command=self._browse_ffmpeg)
        btn_browse_ff.pack(side="left", padx=(0, 6))

        btn_detect_ff = ttk.Button(ffmpeg_row, text="Auto-Detect", style="TButton", command=self._detect_ffmpeg_btn)
        btn_detect_ff.pack(side="right")

        self.ffmpeg_status = tk.Label(main_frame, text="", font=("Segoe UI", 8), fg=c["muted"], bg=c["bg"])
        self.ffmpeg_status.pack(anchor="w", pady=(0, 16))
        self._check_ffmpeg_status()

        # Bottom buttons
        btn_box = tk.Frame(main_frame, bg=c["bg"])
        btn_box.pack(fill="x", side="bottom")

        btn_save = ttk.Button(btn_box, text="💾 Save Preferences", style="Primary.TButton", command=self._save)
        btn_save.pack(side="left")

        btn_cancel = ttk.Button(btn_box, text="Cancel", style="TButton", command=self.destroy)
        btn_cancel.pack(side="right")

    def _browse_dir(self):
        folder = filedialog.askdirectory(initialdir=self.path_var.get())
        if folder:
            self.path_var.set(folder)

    def _browse_ffmpeg(self):
        folder = filedialog.askdirectory(title="Select FFmpeg bin folder")
        if folder:
            self.ffmpeg_var.set(folder)
            self._check_ffmpeg_status()

    def _detect_ffmpeg_btn(self):
        detected = detect_ffmpeg()
        if detected:
            self.ffmpeg_var.set(detected)
            self._check_ffmpeg_status()
            messagebox.showinfo("FFmpeg Found", f"FFmpeg detected at:\n{detected}")
        else:
            messagebox.showwarning("Not Found", "Could not locate FFmpeg automatically. Please select it manually.")

    def _check_ffmpeg_status(self):
        c = get_theme_colors()
        detected = detect_ffmpeg(self.ffmpeg_var.get().strip())
        if detected:
            self.ffmpeg_status.config(text=f"✓ FFmpeg verified: {detected}", fg=c["success"])
        else:
            self.ffmpeg_status.config(text="⚠️ FFmpeg not detected! Merging and audio conversions require FFmpeg.", fg=c["warning"])

    def _save(self):
        new_theme = self.theme_var.get()
        theme_changed = new_theme != config.get("theme")

        config.update({
            "download_dir": self.path_var.get().strip(),
            "theme": new_theme,
            "notifications_enabled": self.notif_var.get(),
            "default_video_quality": self.vquality_var.get(),
            "default_video_format": self.vformat_var.get(),
            "default_audio_bitrate": self.abitrate_var.get(),
            "default_audio_format": self.aformat_var.get(),
            "custom_ffmpeg_path": self.ffmpeg_var.get().strip(),
        })

        if self.on_save_callback:
            self.on_save_callback(theme_changed)

        messagebox.showinfo("Saved", "Preferences saved successfully!")
        self.destroy()

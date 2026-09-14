"""
Main Application Window for YouTube Video Downloader.
"""
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Any

from ..config import (
    config,
    VIDEO_QUALITIES,
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    AUDIO_BITRATES
)
from ..core.downloader import DownloadEngine
from ..core.metadata import MetadataExtractor
from ..core.utils import is_valid_youtube_url
from .theme import apply_theme, get_theme_colors, get_current_theme
from .notifier import notifier
from .components.preview_card import PreviewCard
from .components.progress_panel import ProgressPanel
from .components.batch_panel import BatchPanel
from .components.history_dialog import HistoryDialog
from .components.settings_dialog import SettingsDialog


class MainWindow:
    """Primary application GUI controller."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("YouTube Video & Audio Downloader")
        self.root.geometry("760x720")
        self.root.minsize(680, 580)

        # Core engine
        self.engine = DownloadEngine()
        self.current_metadata: Optional[Dict[str, Any]] = None

        # Apply initial theme
        apply_theme(self.root, config.get("theme", "dark"))

        self._build_ui()

    def _build_ui(self):
        c = get_theme_colors()

        # -------------------------------------------------------------
        # 1. Header Frame
        # -------------------------------------------------------------
        self.header = tk.Frame(self.root, bg=c["bg"], padx=16, pady=12)
        self.header.pack(fill="x")

        title_frame = tk.Frame(self.header, bg=c["bg"])
        title_frame.pack(side="left")

        self.lbl_app_title = tk.Label(
            title_frame,
            text="🎥 YouTube Downloader",
            font=("Segoe UI", 15, "bold"),
            fg=c["fg"],
            bg=c["bg"]
        )
        self.lbl_app_title.pack(anchor="w")

        self.lbl_app_sub = tk.Label(
            title_frame,
            text="Fast, high-quality video & audio downloader powered by yt-dlp",
            font=("Segoe UI", 8),
            fg=c["muted"],
            bg=c["bg"]
        )
        self.lbl_app_sub.pack(anchor="w")

        # Header tool buttons
        btn_header_frame = tk.Frame(self.header, bg=c["bg"])
        btn_header_frame.pack(side="right")

        self.btn_theme = ttk.Button(
            btn_header_frame,
            text="🌙 Theme" if get_current_theme() == "dark" else "☀️ Theme",
            style="TButton",
            command=self._toggle_theme
        )
        self.btn_theme.pack(side="left", padx=(0, 6))

        self.btn_history = ttk.Button(
            btn_header_frame,
            text="📋 History",
            style="TButton",
            command=self._open_history
        )
        self.btn_history.pack(side="left", padx=(0, 6))

        self.btn_settings = ttk.Button(
            btn_header_frame,
            text="⚙️ Settings",
            style="TButton",
            command=self._open_settings
        )
        self.btn_settings.pack(side="left")

        # -------------------------------------------------------------
        # 2. Tabs (Single vs Batch)
        # -------------------------------------------------------------
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        # Tab 1: Single Video
        self.tab_single = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_single, text="  Single Download  ")

        # Tab 2: Batch & Playlist
        self.tab_batch = BatchPanel(
            self.notebook,
            get_download_options_callback=self._get_current_options
        )
        self.notebook.add(self.tab_batch, text="  Batch & Playlist  ")

        # Populate Tab 1: Single Download
        self._build_single_tab()

    def _build_single_tab(self):
        c = get_theme_colors()

        # URL Input Card
        self.url_card = ttk.Frame(self.tab_single, style="Card.TFrame")
        self.url_card.pack(fill="x", padx=6, pady=(10, 6))

        self.url_inner = tk.Frame(self.url_card, bg=c["card_bg"], padx=12, pady=10)
        self.url_inner.pack(fill="x")

        tk.Label(
            self.url_inner,
            text="YouTube Video or Shorts URL:",
            font=("Segoe UI", 9, "bold"),
            fg=c["fg"],
            bg=c["card_bg"]
        ).pack(anchor="w", pady=(0, 4))

        input_row = tk.Frame(self.url_inner, bg=c["card_bg"])
        input_row.pack(fill="x")

        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(
            input_row,
            textvariable=self.url_var,
            font=("Segoe UI", 10)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.url_entry.bind("<Return>", lambda e: self._fetch_metadata())

        self.btn_preview = ttk.Button(
            input_row,
            text="🔍 Preview",
            style="Primary.TButton",
            command=self._fetch_metadata
        )
        self.btn_preview.pack(side="left", padx=(0, 6))

        self.btn_clear_url = ttk.Button(
            input_row,
            text="🧹 Clear",
            style="TButton",
            command=self._clear_single_input
        )
        self.btn_clear_url.pack(side="left")

        # Preview Card (Thumbnail + Metadata)
        self.preview_card = PreviewCard(self.tab_single)
        self.preview_card.pack(fill="x", padx=6, pady=6)

        # Options Card (Type, Quality, Bitrate, Formats, Directory)
        self.options_card = ttk.Frame(self.tab_single, style="Card.TFrame")
        self.options_card.pack(fill="x", padx=6, pady=6)

        self.options_inner = tk.Frame(self.options_card, bg=c["card_bg"], padx=12, pady=10)
        self.options_inner.pack(fill="x")

        # Row 1: Format Type (Radiobuttons)
        type_row = tk.Frame(self.options_inner, bg=c["card_bg"])
        type_row.pack(fill="x", pady=(0, 8))

        tk.Label(
            type_row,
            text="Download Type:",
            font=("Segoe UI", 9, "bold"),
            fg=c["fg"],
            bg=c["card_bg"]
        ).pack(side="left", padx=(0, 15))

        self.type_var = tk.StringVar(value=config.get("default_type", "video"))
        rb_vid = ttk.Radiobutton(
            type_row,
            text="🎬 Video",
            variable=self.type_var,
            value="video",
            command=self._on_type_changed
        )
        rb_vid.pack(side="left", padx=(0, 15))

        rb_aud = ttk.Radiobutton(
            type_row,
            text="🎵 Audio Only",
            variable=self.type_var,
            value="audio",
            command=self._on_type_changed
        )
        rb_aud.pack(side="left")

        # Row 2: Format & Quality Controls
        self.controls_row = tk.Frame(self.options_inner, bg=c["card_bg"])
        self.controls_row.pack(fill="x", pady=(0, 8))

        # Dynamic Quality / Bitrate Label & Combo
        self.lbl_quality = tk.Label(
            self.controls_row,
            text="Resolution:",
            font=("Segoe UI", 9),
            fg=c["fg"],
            bg=c["card_bg"]
        )
        self.lbl_quality.pack(side="left", padx=(0, 6))

        self.quality_var = tk.StringVar(value=config.get("default_video_quality", "best"))
        self.quality_combo = ttk.Combobox(
            self.controls_row,
            textvariable=self.quality_var,
            values=VIDEO_QUALITIES,
            state="readonly",
            width=12
        )
        self.quality_combo.pack(side="left", padx=(0, 18))

        # Dynamic Container / Audio Codec Label & Combo
        self.lbl_format = tk.Label(
            self.controls_row,
            text="Format:",
            font=("Segoe UI", 9),
            fg=c["fg"],
            bg=c["card_bg"]
        )
        self.lbl_format.pack(side="left", padx=(0, 6))

        self.format_var = tk.StringVar(value=config.get("default_video_format", "mp4"))
        self.format_combo = ttk.Combobox(
            self.controls_row,
            textvariable=self.format_var,
            values=VIDEO_FORMATS,
            state="readonly",
            width=10
        )
        self.format_combo.pack(side="left")

        # Row 3: Save Destination
        dest_row = tk.Frame(self.options_inner, bg=c["card_bg"])
        dest_row.pack(fill="x")

        tk.Label(
            dest_row,
            text="Save To:",
            font=("Segoe UI", 9),
            fg=c["fg"],
            bg=c["card_bg"]
        ).pack(side="left", padx=(0, 6))

        self.dest_var = tk.StringVar(value=config.get("download_dir"))
        self.dest_entry = ttk.Entry(
            dest_row,
            textvariable=self.dest_var
        )
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse_dest = ttk.Button(
            dest_row,
            text="Browse...",
            style="TButton",
            command=self._browse_save_dir
        )
        btn_browse_dest.pack(side="right")

        # Progress Panel
        self.progress_panel = ProgressPanel(
            self.tab_single,
            on_download=self._start_single_download,
            on_pause_resume=self._toggle_pause_resume,
            on_cancel=self._cancel_single_download
        )
        self.progress_panel.pack(fill="x", padx=6, pady=(6, 10))

    def _on_type_changed(self):
        """Updates quality and format combobox values when switching between Video and Audio."""
        dtype = self.type_var.get()
        if dtype == "video":
            self.lbl_quality.config(text="Resolution:")
            # If metadata resolutions available, use them, else defaults
            resolutions = VIDEO_QUALITIES
            if self.current_metadata and self.current_metadata.get("available_resolutions"):
                resolutions = self.current_metadata["available_resolutions"]
            self.quality_combo.config(values=resolutions)
            self.quality_var.set(config.get("default_video_quality", "best"))

            self.lbl_format.config(text="Format:")
            self.format_combo.config(values=VIDEO_FORMATS)
            self.format_var.set(config.get("default_video_format", "mp4"))
        else:  # audio
            self.lbl_quality.config(text="Bitrate:")
            self.quality_combo.config(values=AUDIO_BITRATES)
            self.quality_var.set(config.get("default_audio_bitrate", "192"))

            self.lbl_format.config(text="Format:")
            self.format_combo.config(values=AUDIO_FORMATS)
            self.format_var.set(config.get("default_audio_format", "mp3"))

    def _clear_single_input(self):
        self.url_var.set("")
        self.current_metadata = None
        self.preview_card.clear()
        self.progress_panel.reset()

    def _browse_save_dir(self):
        chosen = filedialog.askdirectory(initialdir=self.dest_var.get())
        if chosen:
            self.dest_var.set(chosen)
            config.set("download_dir", chosen)

    def _fetch_metadata(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showinfo("Enter URL", "Please enter a YouTube URL to preview.")
            return

        self.btn_preview.config(state="disabled")
        self.preview_card.set_loading()

        def worker():
            try:
                info = MetadataExtractor.get_info(url)
                thumb_img = None
                if info.get("thumbnail_url"):
                    thumb_img = MetadataExtractor.fetch_thumbnail_image(info["thumbnail_url"])

                def update_ui():
                    self.current_metadata = info
                    self.preview_card.update_preview(info, thumb_img)
                    self.btn_preview.config(state="normal")
                    # Update available resolutions if in video mode
                    if self.type_var.get() == "video" and info.get("available_resolutions"):
                        self.quality_combo.config(values=info["available_resolutions"])

                self.root.after(0, update_ui)
            except Exception as e:
                def on_err():
                    self.btn_preview.config(state="normal")
                    self.preview_card.clear()
                    messagebox.showerror("Error Fetching Info", f"Could not retrieve video information:\n{e}")
                self.root.after(0, on_err)

        threading.Thread(target=worker, daemon=True).start()

    def _get_current_options(self) -> dict:
        dtype = self.type_var.get()
        val = self.quality_var.get()
        return {
            "download_type": dtype,
            "video_quality": val if dtype == "video" else "best",
            "video_format": self.format_var.get() if dtype == "video" else "mp4",
            "audio_format": self.format_var.get() if dtype == "audio" else "mp3",
            "audio_bitrate": val if dtype == "audio" else "192",
            "save_path": self.dest_var.get().strip() or str(config.get("download_dir")),
        }

    def _start_single_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return

        dest = self.dest_var.get().strip()
        if not dest or not os.path.exists(dest):
            try:
                os.makedirs(dest, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Invalid Path", f"Could not access save path:\n{e}")
                return

        opts = self._get_current_options()

        self.progress_panel.set_downloading_state(True)
        self.progress_panel.set_status("Status: Connecting...", "info")

        def on_progress(pct, speed, eta, downloaded, total):
            self.root.after(0, lambda: self.progress_panel.set_progress(pct, speed, eta, downloaded, total))

        def on_status(status_msg):
            self.root.after(0, lambda: self.progress_panel.set_status(f"Status: {status_msg}", "info"))

        def on_success(title, file_path):
            def handle():
                self.progress_panel.set_downloading_state(False)
                self.progress_panel.set_status("Status: Download Completed!", "success")
                notifier.send("Download Finished 🎉", f"{title[:40]}... has finished downloading.")
                res = messagebox.askyesno(
                    "Download Complete!",
                    f"Successfully downloaded:\n{title}\n\nWould you like to open the containing folder?"
                )
                if res and file_path and os.path.exists(file_path):
                    import subprocess
                    subprocess.run(f'explorer /select,"{os.path.abspath(file_path)}"', shell=True)
            self.root.after(0, handle)

        def on_error(err):
            def handle():
                self.progress_panel.set_downloading_state(False)
                self.progress_panel.set_status("Status: Download Failed", "danger")
                notifier.send("Download Failed", f"An error occurred: {err[:60]}")
                messagebox.showerror("Download Error", f"Failed to download:\n{err}")
            self.root.after(0, handle)

        def on_cancel():
            def handle():
                self.progress_panel.set_downloading_state(False)
                self.progress_panel.set_status("Status: Cancelled", "warning")
                messagebox.showinfo("Cancelled", "The download was cancelled.")
            self.root.after(0, handle)

        try:
            self.engine.download_async(
                url=url,
                save_path=dest,
                download_type=opts["download_type"],
                video_quality=opts["video_quality"],
                video_format=opts["video_format"],
                audio_format=opts["audio_format"],
                audio_bitrate=opts["audio_bitrate"],
                on_progress=on_progress,
                on_status=on_status,
                on_success=on_success,
                on_error=on_error,
                on_cancel=on_cancel
            )
        except Exception as e:
            self.progress_panel.set_downloading_state(False)
            messagebox.showerror("Error", str(e))

    def _toggle_pause_resume(self):
        if self.engine.is_paused:
            self.engine.resume()
            self.progress_panel.set_paused_state(False)
        else:
            self.engine.pause()
            self.progress_panel.set_paused_state(True)

    def _cancel_single_download(self):
        if self.engine.is_active:
            if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel the current download?"):
                self.engine.cancel()

    def _toggle_theme(self):
        new_theme = "light" if get_current_theme() == "dark" else "dark"
        config.set("theme", new_theme)
        self.apply_theme_update()

    def apply_theme_update(self):
        theme_name = config.get("theme", "dark")
        apply_theme(self.root, theme_name)
        c = get_theme_colors()

        # Update button text
        self.btn_theme.config(text="🌙 Theme" if theme_name == "dark" else "☀️ Theme")

        # Update root and headers
        self.header.configure(bg=c["bg"])
        self.lbl_app_title.configure(bg=c["bg"], fg=c["fg"])
        self.lbl_app_sub.configure(bg=c["bg"], fg=c["muted"])

        # Update single tab
        self.url_inner.configure(bg=c["card_bg"])
        self.options_inner.configure(bg=c["card_bg"])
        for widget in self.options_inner.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=c["card_bg"])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=c["card_bg"], fg=c["fg"])

        # Update subcomponents
        self.preview_card.update_theme()
        self.progress_panel.update_theme()
        self.tab_batch.update_theme()

    def _open_history(self):
        HistoryDialog(self.root)

    def _open_settings(self):
        def on_save(theme_changed: bool):
            if theme_changed:
                self.apply_theme_update()
            # Update save path display in both Single and Batch tabs
            new_dest = config.get("download_dir")
            self.dest_var.set(new_dest)
            if hasattr(self, "tab_batch") and hasattr(self.tab_batch, "dest_var"):
                self.tab_batch.dest_var.set(new_dest)

        SettingsDialog(self.root, on_save_callback=on_save)

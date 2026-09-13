"""
Progress bar, metrics readout (speed, ETA, size), and action controls (Download, Pause, Resume, Cancel).
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from ..theme import get_theme_colors


class ProgressPanel(ttk.Frame):
    """Panel displaying live download metrics, progress bar, and execution control buttons."""

    def __init__(
        self,
        parent,
        on_download: Optional[Callable] = None,
        on_pause_resume: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self.on_download = on_download
        self.on_pause_resume = on_pause_resume
        self.on_cancel = on_cancel

        self._is_paused = False
        self._build_ui()

    def _build_ui(self):
        c = get_theme_colors()

        self.inner_frame = tk.Frame(self, bg=c["card_bg"], padx=14, pady=12)
        self.inner_frame.pack(fill="x", expand=True)

        # 1. Top row: Status and percentage
        self.status_row = tk.Frame(self.inner_frame, bg=c["card_bg"])
        self.status_row.pack(fill="x", pady=(0, 6))

        self.status_label = tk.Label(
            self.status_row,
            text="Status: Ready",
            font=("Segoe UI", 10, "bold"),
            fg=c["primary"],
            bg=c["card_bg"]
        )
        self.status_label.pack(side="left")

        self.percent_label = tk.Label(
            self.status_row,
            text="0%",
            font=("Segoe UI", 10, "bold"),
            fg=c["fg"],
            bg=c["card_bg"]
        )
        self.percent_label.pack(side="right")

        # 2. Progress Bar
        self.progress_bar = ttk.Progressbar(
            self.inner_frame,
            style="Horizontal.TProgressbar",
            mode="determinate",
            maximum=100
        )
        self.progress_bar.pack(fill="x", pady=(0, 8))

        # 3. Metrics row: Speed, ETA, Downloaded/Total
        self.metrics_row = tk.Frame(self.inner_frame, bg=c["card_bg"])
        self.metrics_row.pack(fill="x", pady=(0, 12))

        self.speed_label = tk.Label(
            self.metrics_row,
            text="📈 Speed: -- KB/s",
            font=("Segoe UI", 9),
            fg=c["muted"],
            bg=c["card_bg"]
        )
        self.speed_label.pack(side="left", padx=(0, 15))

        self.eta_label = tk.Label(
            self.metrics_row,
            text="⏳ ETA: --:--",
            font=("Segoe UI", 9),
            fg=c["muted"],
            bg=c["card_bg"]
        )
        self.eta_label.pack(side="left", padx=(0, 15))

        self.size_label = tk.Label(
            self.metrics_row,
            text="💾 -- / --",
            font=("Segoe UI", 9),
            fg=c["muted"],
            bg=c["card_bg"]
        )
        self.size_label.pack(side="right")

        # 4. Action buttons row
        self.btn_row = tk.Frame(self.inner_frame, bg=c["card_bg"])
        self.btn_row.pack(fill="x")

        self.btn_download = ttk.Button(
            self.btn_row,
            text="⬇️ Download Now",
            style="Primary.TButton",
            command=self._handle_download
        )
        self.btn_download.pack(side="left", padx=(0, 8))

        self.btn_pause = ttk.Button(
            self.btn_row,
            text="⏸️ Pause",
            style="TButton",
            state="disabled",
            command=self._handle_pause_resume
        )
        self.btn_pause.pack(side="left", padx=(0, 8))

        self.btn_cancel = ttk.Button(
            self.btn_row,
            text="❌ Cancel",
            style="Danger.TButton",
            state="disabled",
            command=self._handle_cancel
        )
        self.btn_cancel.pack(side="left")

    def _handle_download(self):
        if self.on_download:
            self.on_download()

    def _handle_pause_resume(self):
        if self.on_pause_resume:
            self.on_pause_resume()

    def _handle_cancel(self):
        if self.on_cancel:
            self.on_cancel()

    def set_downloading_state(self, is_downloading: bool):
        """Toggles controls for active vs idle states."""
        if is_downloading:
            self.btn_download.config(state="disabled")
            self.btn_pause.config(state="normal", text="⏸️ Pause")
            self.btn_cancel.config(state="normal")
            self._is_paused = False
        else:
            self.btn_download.config(state="normal")
            self.btn_pause.config(state="disabled", text="⏸️ Pause")
            self.btn_cancel.config(state="disabled")
            self._is_paused = False

    def set_paused_state(self, is_paused: bool):
        """Updates pause button label and state."""
        self._is_paused = is_paused
        c = get_theme_colors()
        if is_paused:
            self.btn_pause.config(text="▶️ Resume")
            self.set_status("Status: Paused", "warning")
        else:
            self.btn_pause.config(text="⏸️ Pause")
            self.set_status("Status: Downloading...", "info")

    def set_progress(self, percent: float, speed_str: str, eta_str: str, downloaded_str: str, total_str: str):
        """Updates metrics with the latest download chunk report."""
        self.progress_bar["value"] = percent
        self.percent_label.config(text=f"{percent:.1f}%")
        self.speed_label.config(text=f"📈 Speed: {speed_str}")
        self.eta_label.config(text=f"⏳ {eta_str}")
        if downloaded_str and total_str:
            self.size_label.config(text=f"💾 {downloaded_str} / {total_str}")

    def set_status(self, text: str, status_type: str = "info"):
        """Updates the status text with color matching the type."""
        c = get_theme_colors()
        color_map = {
            "info": c["primary"],
            "success": c["success"],
            "warning": c["warning"],
            "danger": c["danger"],
        }
        self.status_label.config(text=text, fg=color_map.get(status_type, c["fg"]))

    def reset(self):
        """Resets the panel to idle values."""
        c = get_theme_colors()
        self.progress_bar["value"] = 0
        self.percent_label.config(text="0%")
        self.speed_label.config(text="📈 Speed: -- KB/s")
        self.eta_label.config(text="⏳ ETA: --:--")
        self.size_label.config(text="💾 -- / --")
        self.status_label.config(text="Status: Ready", fg=c["primary"])
        self.set_downloading_state(False)

    def update_theme(self):
        """Refreshes styling for the current theme."""
        c = get_theme_colors()
        self.inner_frame.configure(bg=c["card_bg"])
        self.status_row.configure(bg=c["card_bg"])
        self.metrics_row.configure(bg=c["card_bg"])
        self.btn_row.configure(bg=c["card_bg"])
        self.status_label.configure(bg=c["card_bg"])
        self.percent_label.configure(bg=c["card_bg"], fg=c["fg"])
        self.speed_label.configure(bg=c["card_bg"], fg=c["muted"])
        self.eta_label.configure(bg=c["card_bg"], fg=c["muted"])
        self.size_label.configure(bg=c["card_bg"], fg=c["muted"])

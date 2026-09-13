"""
Video metadata and thumbnail preview card component.
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any
from PIL import Image, ImageTk
from ..theme import get_theme_colors


class PreviewCard(ttk.Frame):
    """Visual card for video title, thumbnail, duration, and channel metadata."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self.thumbnail_photo: Optional[ImageTk.PhotoImage] = None

        self._build_ui()

    def _build_ui(self):
        c = get_theme_colors()

        # Inner padding frame
        self.inner_frame = tk.Frame(self, bg=c["card_bg"], padx=12, pady=12)
        self.inner_frame.pack(fill="x", expand=True)

        # Left: Thumbnail canvas
        self.thumb_width = 180
        self.thumb_height = 101
        self.thumb_canvas = tk.Canvas(
            self.inner_frame,
            width=self.thumb_width,
            height=self.thumb_height,
            bg=c["surface"],
            highlightthickness=1,
            highlightbackground=c["border"]
        )
        self.thumb_canvas.grid(row=0, column=0, rowspan=4, padx=(0, 14), sticky="nw")
        self._draw_placeholder()

        # Right: Details container
        self.details_frame = tk.Frame(self.inner_frame, bg=c["card_bg"])
        self.details_frame.grid(row=0, column=1, sticky="nsew")
        self.inner_frame.columnconfigure(1, weight=1)

        # Title
        self.title_label = tk.Label(
            self.details_frame,
            text="No Video Selected",
            font=("Segoe UI", 11, "bold"),
            fg=c["fg"],
            bg=c["card_bg"],
            wraplength=380,
            justify="left",
            anchor="w"
        )
        self.title_label.pack(anchor="w", fill="x", pady=(0, 4))

        # Channel
        self.channel_label = tk.Label(
            self.details_frame,
            text="Paste a YouTube link above and click 'Preview' to view details.",
            font=("Segoe UI", 9),
            fg=c["muted"],
            bg=c["card_bg"],
            anchor="w"
        )
        self.channel_label.pack(anchor="w", fill="x", pady=(0, 6))

        # Badges row (Duration, View count)
        self.badges_frame = tk.Frame(self.details_frame, bg=c["card_bg"])
        self.badges_frame.pack(anchor="w", fill="x")

        self.duration_badge = tk.Label(
            self.badges_frame,
            text="⏱️ --:--",
            font=("Segoe UI", 9, "bold"),
            fg=c["primary"],
            bg=c["surface"],
            padx=8,
            pady=2
        )
        self.duration_badge.pack(side="left", padx=(0, 8))

        self.views_badge = tk.Label(
            self.badges_frame,
            text="👁️ -- views",
            font=("Segoe UI", 9),
            fg=c["muted"],
            bg=c["surface"],
            padx=8,
            pady=2
        )
        self.views_badge.pack(side="left")

    def _draw_placeholder(self, text="No Preview"):
        c = get_theme_colors()
        self.thumb_canvas.delete("all")
        self.thumb_canvas.configure(bg=c["surface"], highlightbackground=c["border"])
        self.thumb_canvas.create_text(
            self.thumb_width // 2,
            self.thumb_height // 2,
            text=f"🎬\n{text}",
            font=("Segoe UI", 10),
            fill=c["muted"],
            justify="center"
        )

    def set_loading(self):
        """Displays loading indicator while metadata is fetching."""
        c = get_theme_colors()
        self._draw_placeholder("Loading info...")
        self.title_label.config(text="Fetching video information...", fg=c["fg"])
        self.channel_label.config(text="Contacting YouTube...", fg=c["muted"])
        self.duration_badge.config(text="⏱️ Loading...", fg=c["primary"])
        self.views_badge.config(text="")

    def update_preview(self, info: Dict[str, Any], thumbnail_img: Optional[Image.Image] = None):
        """Updates the card with the retrieved video metadata and thumbnail."""
        c = get_theme_colors()
        title = info.get("title", "Untitled")
        uploader = info.get("uploader", "Unknown Channel")
        duration = info.get("duration_str", "--:--")
        views = info.get("view_count", 0)

        self.title_label.config(text=title, fg=c["fg"])
        self.channel_label.config(text=f"📺 {uploader}", fg=c["muted"])

        if info.get("is_playlist"):
            self.duration_badge.config(text=f"📑 {duration}", fg=c["warning"])
            self.views_badge.config(text="Playlist", fg=c["primary"])
        else:
            self.duration_badge.config(text=f"⏱️ {duration}", fg=c["primary"])
            if views:
                views_str = f"{views:,}" if isinstance(views, int) else str(views)
                self.views_badge.config(text=f"👁️ {views_str} views", fg=c["muted"])
            else:
                self.views_badge.config(text="")

        # Update thumbnail
        if thumbnail_img:
            # Resize image to canvas
            resized = thumbnail_img.copy()
            resized.thumbnail((self.thumb_width, self.thumb_height), Image.Resampling.LANCZOS)
            self.thumbnail_photo = ImageTk.PhotoImage(resized)
            self.thumb_canvas.delete("all")
            self.thumb_canvas.create_image(
                self.thumb_width // 2,
                self.thumb_height // 2,
                image=self.thumbnail_photo
            )
        else:
            self._draw_placeholder("No Thumbnail")

    def clear(self):
        """Resets the preview card to initial empty state."""
        c = get_theme_colors()
        self.thumbnail_photo = None
        self._draw_placeholder()
        self.title_label.config(text="No Video Selected", fg=c["fg"])
        self.channel_label.config(
            text="Paste a YouTube link above and click 'Preview' to view details.",
            fg=c["muted"]
        )
        self.duration_badge.config(text="⏱️ --:--", fg=c["primary"])
        self.views_badge.config(text="👁️ -- views", fg=c["muted"])

    def update_theme(self):
        """Refreshes styling when the theme changes."""
        c = get_theme_colors()
        self.inner_frame.configure(bg=c["card_bg"])
        self.details_frame.configure(bg=c["card_bg"])
        self.badges_frame.configure(bg=c["card_bg"])
        self.thumb_canvas.configure(bg=c["surface"], highlightbackground=c["border"])
        self.title_label.configure(bg=c["card_bg"], fg=c["fg"])
        self.channel_label.configure(bg=c["card_bg"], fg=c["muted"])
        self.duration_badge.configure(bg=c["surface"], fg=c["primary"])
        self.views_badge.configure(bg=c["surface"], fg=c["muted"])
        if not self.thumbnail_photo:
            self._draw_placeholder()

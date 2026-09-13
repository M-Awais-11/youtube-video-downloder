"""
Batch and Playlist download manager with queue table.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import List, Dict, Any, Optional

from ...core.downloader import DownloadEngine
from ...core.metadata import MetadataExtractor
from ...core.utils import is_playlist_url
from ...config import config
from ..theme import get_theme_colors
from ..notifier import notifier


class BatchPanel(ttk.Frame):
    """Panel for batch URL downloads and playlist processing."""

    def __init__(self, parent, get_download_options_callback, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self.get_download_options = get_download_options_callback

        self.queue: List[Dict[str, Any]] = []
        self._is_processing = False
        self._stop_requested = False
        self.current_engine: Optional[DownloadEngine] = None

        self._build_ui()

    def _build_ui(self):
        c = get_theme_colors()

        # Input card
        self.input_card = ttk.Frame(self, style="Card.TFrame")
        self.input_card.pack(fill="x", padx=12, pady=(10, 6))

        self.input_inner = tk.Frame(self.input_card, bg=c["card_bg"], padx=12, pady=10)
        self.input_inner.pack(fill="x")

        tk.Label(
            self.input_inner,
            text="Enter YouTube URLs (one per line) or a Playlist link:",
            font=("Segoe UI", 10, "bold"),
            fg=c["fg"],
            bg=c["card_bg"]
        ).pack(anchor="w", pady=(0, 5))

        self.url_text = tk.Text(
            self.input_inner,
            height=4,
            font=("Segoe UI", 9),
            bg=c["entry_bg"],
            fg=c["entry_fg"],
            insertbackground=c["fg"],
            relief="solid",
            bd=1,
            highlightthickness=0
        )
        self.url_text.pack(fill="x", pady=(0, 8))

        # Button row for Queue
        self.input_btn_row = tk.Frame(self.input_inner, bg=c["card_bg"])
        self.input_btn_row.pack(fill="x")

        self.btn_add = ttk.Button(
            self.input_btn_row,
            text="➕ Add to Queue",
            style="Primary.TButton",
            command=self._handle_add_urls
        )
        self.btn_add.pack(side="left", padx=(0, 8))

        self.btn_clear_text = ttk.Button(
            self.input_btn_row,
            text="🧹 Clear Input",
            style="TButton",
            command=lambda: self.url_text.delete("1.0", tk.END)
        )
        self.btn_clear_text.pack(side="left")

        # Queue Card
        self.queue_card = ttk.Frame(self, style="Card.TFrame")
        self.queue_card.pack(fill="both", expand=True, padx=12, pady=6)

        self.queue_inner = tk.Frame(self.queue_card, bg=c["card_bg"], padx=12, pady=10)
        self.queue_inner.pack(fill="both", expand=True)

        # Queue header
        self.queue_header = tk.Frame(self.queue_inner, bg=c["card_bg"])
        self.queue_header.pack(fill="x", pady=(0, 6))

        self.queue_title = tk.Label(
            self.queue_header,
            text="Download Queue (0 items)",
            font=("Segoe UI", 10, "bold"),
            fg=c["fg"],
            bg=c["card_bg"]
        )
        self.queue_title.pack(side="left")

        self.btn_clear_queue = ttk.Button(
            self.queue_header,
            text="🗑️ Clear Queue",
            style="TButton",
            command=self._clear_queue
        )
        self.btn_clear_queue.pack(side="right")

        # Treeview table
        columns = ("id", "title", "type", "quality", "status")
        self.tree = ttk.Treeview(
            self.queue_inner,
            columns=columns,
            show="headings",
            height=7,
            selectmode="browse"
        )
        self.tree.heading("id", text="#")
        self.tree.heading("title", text="Title / URL")
        self.tree.heading("type", text="Type")
        self.tree.heading("quality", text="Quality")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=35, anchor="center")
        self.tree.column("title", width=320, anchor="w")
        self.tree.column("type", width=70, anchor="center")
        self.tree.column("quality", width=70, anchor="center")
        self.tree.column("status", width=90, anchor="center")

        tree_scroll = ttk.Scrollbar(self.queue_inner, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # Batch Controls & Progress
        self.control_frame = ttk.Frame(self, style="Card.TFrame")
        self.control_frame.pack(fill="x", padx=12, pady=(6, 12))

        self.control_inner = tk.Frame(self.control_frame, bg=c["card_bg"], padx=12, pady=10)
        self.control_inner.pack(fill="x")

        self.batch_status = tk.Label(
            self.control_inner,
            text="Queue Idle",
            font=("Segoe UI", 9, "bold"),
            fg=c["muted"],
            bg=c["card_bg"]
        )
        self.batch_status.pack(anchor="w", pady=(0, 6))

        self.batch_progress = ttk.Progressbar(
            self.control_inner,
            style="Horizontal.TProgressbar",
            mode="determinate",
            maximum=100
        )
        self.batch_progress.pack(fill="x", pady=(0, 8))

        self.btn_batch_start = ttk.Button(
            self.control_inner,
            text="🚀 Start Batch Download",
            style="Primary.TButton",
            command=self._start_batch
        )
        self.btn_batch_start.pack(side="left", padx=(0, 8))

        self.btn_batch_stop = ttk.Button(
            self.control_inner,
            text="⏹️ Stop Batch",
            style="Danger.TButton",
            state="disabled",
            command=self._stop_batch
        )
        self.btn_batch_stop.pack(side="left")

    def _handle_add_urls(self):
        content = self.url_text.get("1.0", tk.END).strip()
        if not content:
            return

        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines:
            return

        opts = self.get_download_options()
        # Check if any URL is a playlist
        for url in lines:
            if is_playlist_url(url):
                # Ask user if they want to expand playlist
                self.btn_add.config(state="disabled", text="Expanding Playlist...")
                threading.Thread(
                    target=self._expand_playlist_and_add,
                    args=(url, opts),
                    daemon=True
                ).start()
            else:
                self._add_item_to_queue(url, url, opts)

        self.url_text.delete("1.0", tk.END)

    def _expand_playlist_and_add(self, playlist_url: str, opts: dict):
        try:
            info = MetadataExtractor.get_info(playlist_url, is_playlist=True)
            entries = info.get("entries", [])
            for e in entries:
                url = e.get("url")
                title = e.get("title", url)
                self.after(0, lambda u=url, t=title: self._add_item_to_queue(u, t, opts))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Playlist Error", f"Could not parse playlist:\n{e}"))
        finally:
            self.after(0, lambda: self.btn_add.config(state="normal", text="➕ Add to Queue"))

    def _add_item_to_queue(self, url: str, title: str, opts: dict):
        item_id = len(self.queue) + 1
        item = {
            "id": item_id,
            "url": url,
            "title": title,
            "type": opts["download_type"],
            "quality": opts["video_quality"] if opts["download_type"] == "video" else f"{opts['audio_bitrate']}k",
            "video_format": opts["video_format"],
            "audio_format": opts["audio_format"],
            "audio_bitrate": opts["audio_bitrate"],
            "save_path": opts["save_path"],
            "status": "Waiting"
        }
        self.queue.append(item)
        self.tree.insert("", "end", iid=str(item_id), values=(
            item_id,
            title,
            item["type"].upper(),
            item["quality"],
            item["status"]
        ))
        self.queue_title.config(text=f"Download Queue ({len(self.queue)} items)")

    def _clear_queue(self):
        if self._is_processing:
            messagebox.showwarning("Warning", "Cannot clear queue while a batch is in progress.")
            return
        self.queue.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.queue_title.config(text="Download Queue (0 items)")
        self.batch_progress["value"] = 0
        self.batch_status.config(text="Queue Idle")

    def _start_batch(self):
        if not self.queue:
            messagebox.showinfo("Queue Empty", "Please add URLs to the queue first.")
            return

        waiting_items = [item for item in self.queue if item["status"] in ("Waiting", "Failed")]
        if not waiting_items:
            messagebox.showinfo("Queue Complete", "All items in queue have already been processed.")
            return

        self._is_processing = True
        self._stop_requested = False
        self.btn_batch_start.config(state="disabled")
        self.btn_batch_stop.config(state="normal")
        self.btn_clear_queue.config(state="disabled")

        threading.Thread(target=self._process_queue_worker, daemon=True).start()

    def _stop_batch(self):
        self._stop_requested = True
        if self.current_engine and self.current_engine.is_active:
            self.current_engine.cancel()
        self.batch_status.config(text="Stopping batch...")

    def _process_queue_worker(self):
        total = len(self.queue)
        completed_count = sum(1 for item in self.queue if item["status"] == "Completed")

        for idx, item in enumerate(self.queue):
            if self._stop_requested:
                break
            if item["status"] == "Completed":
                continue

            # Update UI to Downloading
            item_id_str = str(item["id"])
            item["status"] = "Downloading"
            self.after(0, lambda iid=item_id_str: self.tree.set(iid, "status", "Downloading"))
            self.after(
                0,
                lambda i=idx + 1, t=total, tit=item['title']: self.batch_status.config(
                    text=f"Processing [{i}/{t}]: {tit[:40]}..."
                )
            )

            # Create engine
            engine = DownloadEngine()
            self.current_engine = engine
            done_event = threading.Event()
            success_flag = [False]

            def on_success(title, path):
                success_flag[0] = True
                done_event.set()

            def on_error(err):
                done_event.set()

            def on_cancel():
                done_event.set()

            engine.download_async(
                url=item["url"],
                save_path=item["save_path"],
                download_type=item["type"],
                video_quality=item["quality"].replace("k", ""),
                video_format=item["video_format"],
                audio_format=item["audio_format"],
                audio_bitrate=item["audio_bitrate"],
                on_success=on_success,
                on_error=on_error,
                on_cancel=on_cancel,
            )

            done_event.wait()

            if success_flag[0]:
                item["status"] = "Completed"
                completed_count += 1
                self.after(0, lambda iid=item_id_str: self.tree.set(iid, "status", "Completed"))
            elif self._stop_requested:
                item["status"] = "Cancelled"
                self.after(0, lambda iid=item_id_str: self.tree.set(iid, "status", "Cancelled"))
                break
            else:
                item["status"] = "Failed"
                self.after(0, lambda iid=item_id_str: self.tree.set(iid, "status", "Failed"))

            # Update progress bar
            pct = (completed_count / total) * 100
            self.after(0, lambda p=pct: self.batch_progress.config(value=p))

        self._is_processing = False
        self.current_engine = None

        def finalize():
            self.btn_batch_start.config(state="normal")
            self.btn_batch_stop.config(state="disabled")
            self.btn_clear_queue.config(state="normal")
            status_text = "Batch Finished!" if not self._stop_requested else "Batch Stopped."
            self.batch_status.config(text=f"{status_text} ({completed_count}/{total} completed)")
            notifier.send("Batch Download", f"{status_text} {completed_count} of {total} files completed.")

        self.after(0, finalize)

    def update_theme(self):
        """Refreshes styling when the theme changes."""
        c = get_theme_colors()
        self.input_inner.configure(bg=c["card_bg"])
        self.input_btn_row.configure(bg=c["card_bg"])
        self.queue_inner.configure(bg=c["card_bg"])
        self.queue_header.configure(bg=c["card_bg"])
        self.queue_title.configure(bg=c["card_bg"], fg=c["fg"])
        self.control_inner.configure(bg=c["card_bg"])
        self.batch_status.configure(bg=c["card_bg"], fg=c["muted"])
        self.url_text.configure(
            bg=c["entry_bg"],
            fg=c["entry_fg"],
            insertbackground=c["fg"]
        )

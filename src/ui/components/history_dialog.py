"""
Download History viewer dialog with search, open file/folder, and management tools.
"""
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from ...core.history import history_manager
from ...core.utils import format_bytes
from ..theme import get_theme_colors


class HistoryDialog(tk.Toplevel):
    """Modal dialog displaying the history of downloaded videos/audios."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Download History")
        self.geometry("780x480")
        self.minsize(650, 350)
        self.transient(parent)

        self._build_ui()
        self.load_history()

    def _build_ui(self):
        c = get_theme_colors()
        self.configure(bg=c["bg"])

        # Top bar: Search and Refresh
        top_bar = tk.Frame(self, bg=c["bg"], padx=14, pady=10)
        top_bar.pack(fill="x")

        tk.Label(
            top_bar,
            text="🔍 Search:",
            font=("Segoe UI", 10, "bold"),
            fg=c["fg"],
            bg=c["bg"]
        ).pack(side="left", padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_bar, textvariable=self.search_var, width=35)
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_history())

        btn_refresh = ttk.Button(top_bar, text="🔄 Refresh", style="TButton", command=self.load_history)
        btn_refresh.pack(side="left")

        self.count_label = tk.Label(
            top_bar,
            text="Total: 0",
            font=("Segoe UI", 9),
            fg=c["muted"],
            bg=c["bg"]
        )
        self.count_label.pack(side="right")

        # History Treeview container
        tree_frame = ttk.Frame(self, style="Card.TFrame")
        tree_frame.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        columns = ("id", "title", "type", "quality", "size", "date", "status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="#")
        self.tree.heading("title", text="Title")
        self.tree.heading("type", text="Type")
        self.tree.heading("quality", text="Quality")
        self.tree.heading("size", text="Size")
        self.tree.heading("date", text="Date")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("title", width=280, anchor="w")
        self.tree.column("type", width=60, anchor="center")
        self.tree.column("quality", width=70, anchor="center")
        self.tree.column("size", width=80, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("status", width=80, anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self._open_file())

        # Action Buttons
        btn_frame = tk.Frame(self, bg=c["bg"], padx=14, pady=10)
        btn_frame.pack(fill="x")

        btn_open_file = ttk.Button(btn_frame, text="▶️ Play / Open File", style="Primary.TButton", command=self._open_file)
        btn_open_file.pack(side="left", padx=(0, 8))

        btn_open_folder = ttk.Button(btn_frame, text="📁 Show in Folder", style="TButton", command=self._open_folder)
        btn_open_folder.pack(side="left", padx=(0, 8))

        btn_delete = ttk.Button(btn_frame, text="🗑️ Delete Entry", style="TButton", command=self._delete_selected)
        btn_delete.pack(side="left", padx=(0, 8))

        btn_clear = ttk.Button(btn_frame, text="🧹 Clear All History", style="Danger.TButton", command=self._clear_all)
        btn_clear.pack(side="left")

        btn_close = ttk.Button(btn_frame, text="Close", style="TButton", command=self.destroy)
        btn_close.pack(side="right")

    def load_history(self):
        """Loads records from SQLite into the treeview."""
        query = self.search_var.get()
        records = history_manager.get_history(search_query=query)

        for item in self.tree.get_children():
            self.tree.delete(item)

        self._record_map = {}
        for r in records:
            rec_id = r["id"]
            self._record_map[str(rec_id)] = r
            size_str = format_bytes(r["file_size"]) if r.get("file_size") else "--"
            self.tree.insert("", "end", iid=str(rec_id), values=(
                rec_id,
                r.get("title") or "Unknown",
                (r.get("type") or "").upper(),
                r.get("quality") or "",
                size_str,
                r.get("created_at") or "",
                r.get("status") or "Unknown"
            ))

        self.count_label.config(text=f"Total: {len(records)}")

    def _get_selected_record(self) -> Optional[dict]:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Select Entry", "Please select an item from the history list.")
            return None
        rec_id_str = selection[0]
        return self._record_map.get(rec_id_str)

    def _open_file(self):
        rec = self._get_selected_record()
        if not rec:
            return
        path = rec.get("file_path")
        if not path or not os.path.exists(path):
            messagebox.showerror("File Not Found", f"The downloaded file was moved or deleted:\n{path}")
            return

        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def _open_folder(self):
        rec = self._get_selected_record()
        if not rec:
            return
        path = rec.get("file_path")
        if path and os.path.exists(path):
            subprocess.run(f'explorer /select,"{os.path.abspath(path)}"', shell=True)
        else:
            # Fallback to download folder
            dl_dir = config.get("download_dir")
            if os.path.exists(dl_dir):
                subprocess.run(f'explorer "{os.path.abspath(dl_dir)}"', shell=True)
            else:
                messagebox.showerror("Error", "Download location does not exist.")

    def _delete_selected(self):
        rec = self._get_selected_record()
        if not rec:
            return
        history_manager.delete_record(rec["id"])
        self.load_history()

    def _clear_all(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to delete all download history?"):
            history_manager.clear_all()
            self.load_history()

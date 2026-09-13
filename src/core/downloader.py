"""
Core Downloader engine built on yt-dlp with pause, resume, cancel, and progress tracking.
"""
import os
import time
import threading
from pathlib import Path
from typing import Callable, Optional, Dict, Any

import yt_dlp

from .utils import (
    sanitize_filename,
    detect_ffmpeg,
    format_bytes,
    format_speed,
    format_seconds
)
from .history import history_manager
from ..config import config


class DownloadCancelledException(Exception):
    """Raised when a download is aborted by user request."""
    pass


class DownloadEngine:
    """Manages individual or queued download executions with control signals."""

    def __init__(self):
        self._pause_event = threading.Event()
        self._pause_event.set()  # set means running; clear means paused
        self._cancel_requested = False
        self._is_active = False
        self._current_thread: Optional[threading.Thread] = None

        self.last_filename: Optional[str] = None
        self.history_record_id: Optional[int] = None

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_paused(self) -> bool:
        return not self._pause_event.is_set()

    def pause(self):
        """Pauses the ongoing download."""
        if self._is_active:
            self._pause_event.clear()

    def resume(self):
        """Resumes the paused download."""
        if self._is_active:
            self._pause_event.set()

    def cancel(self):
        """Signals cancellation to the download thread."""
        if self._is_active:
            self._cancel_requested = True
            # Unpause so it wakes up and terminates immediately
            self._pause_event.set()

    def download_async(
        self,
        url: str,
        save_path: str,
        download_type: str = "video",
        video_quality: str = "best",
        video_format: str = "mp4",
        audio_format: str = "mp3",
        audio_bitrate: str = "192",
        on_progress: Optional[Callable[[float, str, str, str, str], None]] = None,
        on_status: Optional[Callable[[str], None]] = None,
        on_success: Optional[Callable[[str, str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
    ):
        """Starts a download task in a separate daemon thread."""
        if self._is_active:
            raise RuntimeError("A download is already in progress.")

        self._pause_event.set()
        self._cancel_requested = False
        self._is_active = True
        self.last_filename = None

        self._current_thread = threading.Thread(
            target=self._run_download,
            args=(
                url,
                save_path,
                download_type,
                video_quality,
                video_format,
                audio_format,
                audio_bitrate,
                on_progress,
                on_status,
                on_success,
                on_error,
                on_cancel,
            ),
            daemon=True
        )
        self._current_thread.start()

    def _run_download(
        self,
        url: str,
        save_path: str,
        download_type: str,
        video_quality: str,
        video_format: str,
        audio_format: str,
        audio_bitrate: str,
        on_progress: Optional[Callable],
        on_status: Optional[Callable],
        on_success: Optional[Callable],
        on_error: Optional[Callable],
        on_cancel: Optional[Callable],
    ):
        ffmpeg_dir = detect_ffmpeg(config.get("custom_ffmpeg_path"))
        title_for_history = "YouTube Download"
        final_filepath = ""
        total_file_size = 0

        # Create history record early with 'Downloading' status
        self.history_record_id = history_manager.add_record(
            title="Fetching details...",
            url=url,
            download_type=download_type,
            quality=video_quality if download_type == "video" else f"{audio_bitrate} kbps",
            output_format=video_format if download_type == "video" else audio_format,
            file_size=0,
            file_path="",
            status="Downloading"
        )

        def progress_hook(d):
            # Check for cancellation
            if self._cancel_requested:
                raise DownloadCancelledException("Download cancelled by user.")

            # Check for pause
            while not self._pause_event.is_set():
                if self._cancel_requested:
                    raise DownloadCancelledException("Download cancelled by user.")
                if on_status:
                    on_status("Paused")
                time.sleep(0.2)

            status = d.get("status")
            if status == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                speed = d.get("speed")
                eta = d.get("eta")

                percent = (downloaded / total * 100) if total > 0 else 0.0

                speed_str = format_speed(speed)
                eta_str = f"ETA: {format_seconds(eta)}" if eta else "ETA: --:--"
                downloaded_str = format_bytes(downloaded)
                total_str = format_bytes(total)

                if on_progress:
                    on_progress(percent, speed_str, eta_str, downloaded_str, total_str)
                if on_status:
                    on_status("Downloading...")

            elif status == "finished":
                filename = d.get("filename")
                if filename:
                    self.last_filename = filename
                if on_progress:
                    on_progress(100.0, "Done", "00:00", "", "")
                if on_status:
                    on_status("Processing / Merging...")

        def postprocessor_hook(d):
            if self._cancel_requested:
                raise DownloadCancelledException("Download cancelled by user.")
            if d.get("status") == "started" and on_status:
                on_status("Post-processing with FFmpeg...")

        # Setup yt-dlp options
        outtmpl = os.path.join(save_path, "%(title).150B.%(ext)s")

        ydl_opts: Dict[str, Any] = {
            "outtmpl": outtmpl,
            "progress_hooks": [progress_hook],
            "postprocessor_hooks": [postprocessor_hook],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "windowsfilenames": True,  # automatic sanitize on Windows
        }

        if ffmpeg_dir:
            ydl_opts["ffmpeg_location"] = ffmpeg_dir

        if download_type == "video":
            if video_quality == "best":
                format_spec = f"bestvideo+bestaudio/best"
            else:
                format_spec = f"bestvideo[height<={video_quality}]+bestaudio/best"

            ydl_opts["format"] = format_spec
            ydl_opts["merge_output_format"] = video_format
        else:  # audio only
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": audio_bitrate,
                }
            ]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract title for history
                try:
                    info_dict = ydl.extract_info(url, download=True)
                    if info_dict:
                        title_for_history = info_dict.get("title", title_for_history)
                        # Determine final file path
                        if "_filename" in info_dict:
                            final_filepath = info_dict["_filename"]
                        elif self.last_filename:
                            final_filepath = self.last_filename

                        # Adjust extension for audio postprocessing
                        if download_type == "audio" and final_filepath:
                            final_filepath = str(Path(final_filepath).with_suffix(f".{audio_format}"))

                        if final_filepath and os.path.exists(final_filepath):
                            total_file_size = os.path.getsize(final_filepath)
                except DownloadCancelledException:
                    raise
                except Exception:
                    # If extract_info with download=True errored, re-raise
                    raise

            # Success
            self._is_active = False
            history_manager.update_status(
                self.history_record_id,
                status="Completed",
                file_path=final_filepath,
                file_size=total_file_size
            )
            # Update title in history
            with history_manager._get_connection() as conn:
                conn.execute(
                    "UPDATE download_history SET title = ? WHERE id = ?",
                    (title_for_history, self.history_record_id)
                )
                conn.commit()

            if on_status:
                on_status("Completed")
            if on_success:
                on_success(title_for_history, final_filepath)

        except DownloadCancelledException:
            self._is_active = False
            history_manager.update_status(self.history_record_id, status="Cancelled")
            # Cleanup partial files
            self._cleanup_partial_files(save_path)
            if on_status:
                on_status("Cancelled")
            if on_cancel:
                on_cancel()

        except Exception as e:
            self._is_active = False
            err_msg = str(e)
            history_manager.update_status(self.history_record_id, status="Failed")
            if on_status:
                on_status("Failed")
            if on_error:
                on_error(err_msg)

    def _cleanup_partial_files(self, directory: str):
        """Removes temporary .part and .ytdl files created during an aborted download."""
        try:
            dir_path = Path(directory)
            for part in dir_path.glob("*.part"):
                part.unlink(missing_ok=True)
            for ytdl in dir_path.glob("*.ytdl"):
                ytdl.unlink(missing_ok=True)
        except Exception as e:
            print(f"[DownloadEngine] Clean up error: {e}")

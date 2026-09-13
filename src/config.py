"""
Configuration and settings management for YouTube Video Downloader.
"""
import os
import json
from pathlib import Path

# Paths
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DOWNLOAD_DIR = PROJECT_ROOT / "downloads"
SETTINGS_FILE = DATA_DIR / "settings.json"
HISTORY_DB_FILE = DATA_DIR / "history.db"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_SETTINGS = {
    "download_dir": str(DEFAULT_DOWNLOAD_DIR),
    "theme": "dark",
    "default_type": "video",
    "default_video_quality": "best",
    "default_video_format": "mp4",
    "default_audio_format": "mp3",
    "default_audio_bitrate": "192",
    "custom_ffmpeg_path": "",
    "notifications_enabled": True,
    "auto_preview": True,
    "max_concurrent_downloads": 2,
}

VIDEO_QUALITIES = ["best", "2160", "1440", "1080", "720", "480", "360"]
VIDEO_FORMATS = ["mp4", "mkv", "webm"]
AUDIO_FORMATS = ["mp3", "m4a", "wav", "aac", "flac"]
AUDIO_BITRATES = ["64", "128", "192", "256", "320"]


class Config:
    """Manages application settings and persistence."""

    def __init__(self):
        self._settings = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        """Loads settings from JSON file if it exists."""
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._settings.update(data)
            except Exception as e:
                print(f"[Config] Error loading settings: {e}")

    def save(self):
        """Saves current settings to JSON file."""
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4)
        except Exception as e:
            print(f"[Config] Error saving settings: {e}")

    def get(self, key, default=None):
        """Gets a configuration setting."""
        return self._settings.get(key, default)

    def set(self, key, value):
        """Sets a configuration setting and persists it."""
        self._settings[key] = value
        self.save()

    def update(self, new_settings: dict):
        """Updates multiple settings and persists them."""
        self._settings.update(new_settings)
        self.save()

    def all(self) -> dict:
        """Returns a copy of all settings."""
        return dict(self._settings)


# Global singleton instance
config = Config()

"""
Utility functions for file sanitization, formatting, and FFmpeg detection.
"""
import os
import re
import shutil
from pathlib import Path
from typing import Optional

# Windows illegal characters
ILLEGAL_CHARS_PATTERN = re.compile(r'[\\/*?:"<>|\x00-\x1f]')
RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}


def sanitize_filename(filename: str, max_length: int = 150) -> str:
    """
    Sanitizes a string to make it safe for use as a Windows/Unix filename.
    Removes invalid characters, strips leading/trailing spaces and dots,
    and prevents reserved Windows device names.
    """
    if not filename:
        return "untitled"

    # Replace illegal characters with an underscore
    clean = ILLEGAL_CHARS_PATTERN.sub("_", filename)

    # Collapse multiple underscores or spaces
    clean = re.sub(r'[\s_]+', ' ', clean).strip(' .')

    # Truncate length
    if len(clean) > max_length:
        clean = clean[:max_length].rstrip(' .')

    # Check for reserved Windows file names
    base_name = clean.split('.')[0].upper()
    if base_name in RESERVED_NAMES:
        clean = f"_{clean}"

    return clean or "download"


def detect_ffmpeg(custom_path: Optional[str] = None) -> Optional[str]:
    """
    Detects the FFmpeg binary or directory.
    Checks custom path, system PATH, and known WinGet/common install directories.
    Returns the path to the directory containing ffmpeg or the executable path.
    """
    # 1. Custom path specified in settings
    if custom_path and os.path.exists(custom_path):
        p = Path(custom_path)
        if p.is_file() and p.stem.lower() == "ffmpeg":
            return str(p.parent)
        if (p / "ffmpeg.exe").exists() or (p / "ffmpeg").exists():
            return str(p)

    # 2. System PATH
    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg:
        return str(Path(which_ffmpeg).parent)

    # 3. Known WinGet Gyan.FFmpeg install paths
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_pkgs = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_pkgs.exists():
            for match in winget_pkgs.glob("**/ffmpeg-*-full_build/bin"):
                if (match / "ffmpeg.exe").exists():
                    return str(match)
            for match in winget_pkgs.glob("**/ffmpeg.exe"):
                return str(match.parent)

    # 4. Standard Program Files / C: paths
    common_locations = [
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\Program Files (x86)\ffmpeg\bin",
    ]
    for loc in common_locations:
        if os.path.isdir(loc) and (Path(loc) / "ffmpeg.exe").exists():
            return loc

    return None


def format_bytes(bytes_count: Optional[float]) -> str:
    """Formats bytes into human readable B, KB, MB, GB."""
    if bytes_count is None or bytes_count < 0:
        return "Unknown size"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(bytes_count)

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"


def format_speed(bytes_per_sec: Optional[float]) -> str:
    """Formats speed in bytes/sec to readable speed string."""
    if not bytes_per_sec or bytes_per_sec <= 0:
        return "-- KB/s"

    if bytes_per_sec >= 1024 * 1024:
        return f"{bytes_per_sec / (1024 * 1024):.2f} MB/s"
    return f"{bytes_per_sec / 1024:.1f} KB/s"


def format_seconds(seconds: Optional[float]) -> str:
    """Formats seconds into HH:MM:SS or MM:SS."""
    if seconds is None or seconds < 0:
        return "--:--"

    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def is_valid_youtube_url(url: str) -> bool:
    """Validates whether the given string is a YouTube URL."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    pattern = r'^(https?://)?(www\.|m\.)?(youtube\.com|youtu\.be)/(watch\?v=|embed/|v/|shorts/|playlist\?|.*[?&]v=)?[a-zA-Z0-9_\-\?=&]+'
    return bool(re.match(pattern, url))


def is_playlist_url(url: str) -> bool:
    """Checks if a URL contains a YouTube playlist parameter."""
    if not url:
        return False
    return "list=" in url or "/playlist" in url

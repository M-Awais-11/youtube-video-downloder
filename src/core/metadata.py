"""
Video and Playlist metadata extraction and thumbnail retrieval.
"""
import io
import requests
import yt_dlp
from PIL import Image, ImageTk
from typing import Dict, Any, Optional, List
from .utils import format_seconds, detect_ffmpeg
from ..config import config


class MetadataExtractor:
    """Extracts YouTube video & playlist metadata and thumbnails."""

    @staticmethod
    def get_info(url: str, is_playlist: bool = False) -> Dict[str, Any]:
        """
        Extracts metadata for a YouTube URL using yt-dlp.
        Returns a structured dictionary of information.
        """
        ffmpeg_dir = detect_ffmpeg(config.get("custom_ffmpeg_path"))

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": "in_playlist" if is_playlist else False,
        }
        if ffmpeg_dir:
            ydl_opts["ffmpeg_location"] = ffmpeg_dir

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            raise ValueError("Failed to retrieve metadata from URL.")

        # Check if result is a playlist
        if "entries" in info:
            entries = list(info.get("entries") or [])
            first_thumb = None
            if entries and isinstance(entries[0], dict):
                first_thumb = entries[0].get("thumbnail") or entries[0].get("thumbnails", [{}])[-1].get("url")

            return {
                "is_playlist": True,
                "title": info.get("title", "YouTube Playlist"),
                "uploader": info.get("uploader", "Various Artists / Channels"),
                "playlist_count": len(entries),
                "entries": [
                    {
                        "url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
                        "title": e.get("title", "Unknown Title"),
                        "duration": e.get("duration", 0),
                        "id": e.get("id"),
                    }
                    for e in entries if isinstance(e, dict)
                ],
                "thumbnail_url": info.get("thumbnail") or first_thumb,
                "duration_str": f"{len(entries)} items",
                "available_resolutions": ["best", "1080", "720", "480", "360"],
            }

        # Single video
        resolutions = set()
        formats = info.get("formats", [])
        for f in formats:
            height = f.get("height")
            if height and isinstance(height, int) and height >= 144:
                resolutions.add(height)

        sorted_res = sorted(list(resolutions), reverse=True)
        res_strings = [str(r) for r in sorted_res]
        if "best" not in res_strings:
            res_strings.insert(0, "best")

        # Pick best thumbnail
        thumbnails = info.get("thumbnails", [])
        thumb_url = info.get("thumbnail")
        if not thumb_url and thumbnails:
            thumb_url = thumbnails[-1].get("url")

        return {
            "is_playlist": False,
            "id": info.get("id"),
            "title": info.get("title", "Untitled Video"),
            "uploader": info.get("uploader") or info.get("channel", "Unknown Channel"),
            "duration": info.get("duration", 0),
            "duration_str": format_seconds(info.get("duration")),
            "view_count": info.get("view_count", 0),
            "thumbnail_url": thumb_url,
            "available_resolutions": res_strings if res_strings else ["best", "1080", "720", "480", "360"],
            "webpage_url": info.get("webpage_url", url),
        }

    @staticmethod
    def fetch_thumbnail_image(url: str, size: tuple = (200, 112)) -> Optional[Image.Image]:
        """
        Downloads thumbnail image from URL and resizes it to the target dimensions.
        Returns a PIL Image or None on failure.
        """
        if not url:
            return None
        try:
            resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            img_data = io.BytesIO(resp.content)
            img = Image.open(img_data)
            img = img.convert("RGBA")
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Create standard sized background container
            canvas = Image.new("RGBA", size, (0, 0, 0, 0))
            offset_x = (size[0] - img.width) // 2
            offset_y = (size[1] - img.height) // 2
            canvas.paste(img, (offset_x, offset_y))
            return canvas
        except Exception as e:
            print(f"[MetadataExtractor] Thumbnail fetch error: {e}")
            return None

# 🎥 YouTube Video & Audio Downloader Pro

A modern, high-performance desktop application built with Python, Tkinter, `yt-dlp`, and FFmpeg. Supports single and batch downloads, playlist fetching, live speed and ETA monitoring, video metadata & thumbnail previews, pause/resume, and dark/light themes.

---

## ✨ Features

- ⏸️ **Pause & Resume Downloads**: Safely pause ongoing downloads and resume them anytime without losing progress.
- ❌ **Cancel Downloads**: Cleanly cancel downloads with automatic cleanup of partial files.
- 📋 **Download History**: SQLite-backed history tracking with search filters, "Open File", and "Show in Folder" actions.
- 🔎 **Video Metadata Preview**: Automatically retrieves video title, channel, duration, and view count before downloading.
- 🖼️ **Thumbnail Preview**: Displays the video's high-resolution thumbnail directly in the interface.
- 📦 **Batch URL Downloading**: Paste multiple URLs to download them sequentially in a queue.
- 📑 **Playlist Support**: Enter a playlist URL to parse and queue all videos automatically.
- 🎚️ **Custom Audio Bitrates**: Choose from 64 kbps, 128 kbps, 192 kbps, 256 kbps, or 320 kbps.
- 🎞️ **Multiple Video Formats**: Support for MP4, MKV, and WEBM in various resolutions (4K, 2K, 1080p, 720p, 480p, 360p, Best).
- 🎵 **Multiple Audio Formats**: Support for MP3, M4A, WAV, AAC, and FLAC.
- 🌙 **Dark & Light Mode**: Modern UI with a one-click theme switcher and persistent user preferences.
- 📈 **Real-Time Download Speed**: Displays live download speed (e.g., `5.42 MB/s`).
- ⏳ **Estimated Time Remaining (ETA)**: Live calculation of time left for the current download.
- 🔔 **Desktop Notifications**: Native Windows notifications on download start, completion, or error.
- 🧹 **Automatic Filename Sanitization**: Strips illegal OS characters and reserved device names for safe file saving.
- 🖥️ **Responsive High-DPI GUI**: Crisp typography and layout that scales cleanly on high-resolution displays.
- ⚙️ **Advanced Settings**: Configure default download directories, preferred formats, FFmpeg path auto-detection, and notifications.

---

## 📁 Project Structure

```text
Youtube_video_downloader/
├── src/
│   ├── __init__.py
│   ├── config.py              # Settings persistence (settings.json) & default configurations
│   ├── core/
│   │   ├── __init__.py
│   │   ├── downloader.py      # Core download engine (yt-dlp, pause/resume, cancel, progress hooks)
│   │   ├── metadata.py        # Video & playlist metadata extractor and thumbnail downloader
│   │   ├── history.py         # SQLite database manager for download history
│   │   └── utils.py           # Filename sanitization, speed/ETA/size formatters, FFmpeg detection
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py     # Main application window & event controllers
│       ├── theme.py           # Dark & Light theme styling system (colors & ttk styles)
│       ├── notifier.py        # Desktop notification handler (Windows Toast)
│       └── components/
│           ├── __init__.py
│           ├── preview_card.py    # Video thumbnail & metadata preview card
│           ├── progress_panel.py  # Progress bar, speed, ETA, pause/resume/cancel buttons
│           ├── batch_panel.py     # Multi-URL batch & playlist download queue view
│           ├── history_dialog.py  # Download history modal with search & quick actions
│           └── settings_dialog.py # Settings modal (FFmpeg path, defaults, notifications)
├── downloads/                 # Default destination directory for downloaded media
├── data/                      # Local application storage (history.db, settings.json)
├── main.py                    # Application entry point
├── video-downloader.py        # Backward-compatible redirect launcher
├── requirements.txt           # Project dependencies
├── .gitignore                 # Git ignore rules for media, caches, and local databases
└── README.md                  # Project documentation
```

---

## 🚀 Installation & Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **FFmpeg**: Required for merging video/audio streams and extracting audio.
  - *Note:* The application automatically searches your system `PATH` and WinGet directories for FFmpeg. You can also specify a custom path in the Settings window.

### 2. Set Up Virtual Environment (Optional)

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Launch via the primary entry point:
```bash
python main.py
```
Or via the legacy script (fully compatible):
```bash
python video-downloader.py
```

---

## 📖 Usage Guide

### Single Download Mode
1. Paste any YouTube video or Shorts link into the URL input box.
2. Click **Preview** (or press `Enter`) to inspect the title, channel, duration, and thumbnail.
3. Select **Video** or **Audio Only**, choose your desired quality/bitrate and format.
4. Click **Download Now**.
5. You can **Pause ⏸️**, **Resume ▶️**, or **Cancel ❌** the download at any time.

### Batch & Playlist Mode
1. Switch to the **Batch & Playlist** tab.
2. Paste multiple YouTube links (one per line) or a Playlist URL.
3. Click **Add to Queue** (if a playlist link is provided, it will automatically expand into individual items).
4. Click **Start Batch Download** to process the queue sequentially.

### Viewing History
- Click the **📋 History** button in the header.
- Search past downloads, double-click to play, or click **Show in Folder** to locate the file in Windows Explorer.

---

## 👨‍💻 Author

**M. AWAIS AFZAL**  
Computer Science | AI/ML | Computer Vision | Software Development  
GitHub: [M-Awais-11](https://github.com/M-Awais-11)

---

## 📜 License & Disclaimer
This project is developed for educational and personal use only. Please respect the copyright of content creators and adhere to YouTube's terms of service.

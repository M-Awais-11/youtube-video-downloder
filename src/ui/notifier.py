"""
Desktop notification service for Windows.
"""
import os
import sys
import subprocess
import threading
from typing import Optional
from ..config import config

try:
    import winsound
except ImportError:
    winsound = None


class Notifier:
    """Delivers native Windows desktop notifications safely in background threads."""

    @classmethod
    def send(cls, title: str, message: str, sound: bool = True):
        """Dispatches notification if notifications are enabled in settings."""
        if not config.get("notifications_enabled", True):
            return

        # Sound beep
        if sound and winsound:
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass

        # Windows toast in background thread
        if sys.platform == "win32":
            threading.Thread(
                target=cls._send_windows_toast,
                args=(title, message),
                daemon=True
            ).start()

    @staticmethod
    def _send_windows_toast(title: str, message: str):
        """Sends native Windows 10/11 toast notification using PowerShell."""
        clean_title = title.replace('"', '`"').replace("'", "''")
        clean_msg = message.replace('"', '`"').replace("'", "''")

        ps_script = f"""
        try {{
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $xmlString = @"
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>{clean_title}</text>
                        <text>{clean_msg}</text>
                    </binding>
                </visual>
            </toast>
"@
            $xmlDoc = [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]::new()
            $xmlDoc.LoadXml($xmlString)
            $toast = [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime]::new($xmlDoc)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("YouTube Downloader").Show($toast)
        }} catch {{
            # Silently handle if notification center is disabled
        }}
        """

        startupinfo = None
        creationflags = 0
        if hasattr(subprocess, "STARTUPINFO"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=4,
                capture_output=True
            )
        except Exception:
            pass


notifier = Notifier()

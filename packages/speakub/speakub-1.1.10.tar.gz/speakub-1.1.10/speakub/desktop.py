#!/usr/bin/env python3
"""
Desktop integration utilities for SpeakUB
"""

import sys
from pathlib import Path


def install_desktop_entry() -> bool:
    """
    Install .desktop file for SpeakUB
    Returns True if successful, False otherwise
    """
    try:
        desktop_dir = Path.home() / ".local/share/applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)

        desktop_file = desktop_dir / "speakub.desktop"

        content = """\
[Desktop Entry]
Type=Application
Name=SpeakUB
Comment=EPUB Reader with TTS
Exec=speakub %f
Terminal=true
Categories=Office;Education;
MimeType=application/epub+zip;
Icon=book
"""

        desktop_file.write_text(content)
        desktop_file.chmod(0o755)

        print(f"Desktop entry installed: {desktop_file}")
        return True

    except Exception as e:
        print(f"Warning: Failed to install desktop entry: {e}", file=sys.stderr)
        return False


def check_desktop_installed() -> bool:
    """Check if desktop entry is already installed"""
    desktop_file = Path.home() / ".local/share/applications/speakub.desktop"
    return desktop_file.exists()

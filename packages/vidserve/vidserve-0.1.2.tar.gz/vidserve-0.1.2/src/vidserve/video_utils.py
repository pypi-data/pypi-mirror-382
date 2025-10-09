"""Utilities for video scanning and thumbnail generation."""

import os
import tempfile
from pathlib import Path

import cv2
from PIL import Image


VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv", ".m4v"}


def get_video_files(directory: str | Path) -> list[Path]:
    """Scan directory for video files.

    Args:
        directory: Directory path to scan for videos

    Returns:
        List of Path objects for found video files
    """
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        return []

    video_files = []
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
            video_files.append(file_path)

    return sorted(video_files)


def get_video_duration(video_path: Path) -> float | None:
    """Get video duration in seconds.

    Args:
        video_path: Path to video file

    Returns:
        Duration in seconds or None if unable to read
    """
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()

        if fps > 0:
            return frame_count / fps
        return None
    except Exception:
        return None


def format_duration(seconds: float | None) -> str:
    """Format duration in seconds to MM:SS or HH:MM:SS.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds is None:
        return "Unknown"

    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def generate_thumbnail(video_path: Path, output_dir: Path, max_size: tuple[int, int] = (320, 180)) -> Path | None:
    """Generate a thumbnail from the middle frame of a video.

    Args:
        video_path: Path to video file
        output_dir: Directory to save thumbnail
        max_size: Maximum thumbnail dimensions (width, height)

    Returns:
        Path to generated thumbnail or None if failed
    """
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return None

        # Get total frame count and seek to middle
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        middle_frame = frame_count // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)

        # Read frame
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            return None

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create PIL Image and resize
        img = Image.fromarray(frame_rgb)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save thumbnail
        thumbnail_name = f"{video_path.stem}.jpg"
        thumbnail_path = output_dir / thumbnail_name
        img.save(thumbnail_path, "JPEG", quality=85)

        return thumbnail_path
    except Exception as e:
        print(f"Error generating thumbnail for {video_path.name}: {e}")
        return None


def get_thumbnail_cache_dir() -> Path:
    """Get or create thumbnail cache directory.

    Returns:
        Path to thumbnail cache directory
    """
    cache_dir = Path(tempfile.gettempdir()) / "vidserve_thumbnails"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


def generate_all_thumbnails(video_files: list[Path]) -> dict[str, Path]:
    """Generate thumbnails for all video files.

    Args:
        video_files: List of video file paths

    Returns:
        Dictionary mapping video filenames to thumbnail paths
    """
    cache_dir = get_thumbnail_cache_dir()
    thumbnails = {}

    print(f"Generating thumbnails for {len(video_files)} videos...")
    for i, video_path in enumerate(video_files, 1):
        print(f"  [{i}/{len(video_files)}] {video_path.name}")
        thumbnail_path = generate_thumbnail(video_path, cache_dir)
        if thumbnail_path:
            thumbnails[video_path.name] = thumbnail_path

    print(f"Generated {len(thumbnails)} thumbnails")
    return thumbnails

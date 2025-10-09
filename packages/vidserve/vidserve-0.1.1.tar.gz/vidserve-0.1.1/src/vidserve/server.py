"""Flask server for video streaming."""

import os
import json
from pathlib import Path

from flask import Flask, render_template, send_file, Response, request, abort

from vidserve.video_utils import get_video_duration, format_duration


def get_video_mimetype(filename: str) -> str:
    """Determine MIME type based on video file extension.

    Args:
        filename: Video filename

    Returns:
        MIME type string
    """
    ext = Path(filename).suffix.lower()
    mime_types = {
        ".mp4": "video/mp4",
        ".m4v": "video/mp4",
        ".avi": "video/x-msvideo",
        ".mov": "video/quicktime",
        ".mkv": "video/x-matroska",
        ".webm": "video/webm",
        ".flv": "video/x-flv",
        ".wmv": "video/x-ms-wmv",
    }
    return mime_types.get(ext, "video/mp4")


def create_app(video_dir: Path, thumbnails: dict[str, Path]) -> Flask:
    """Create and configure Flask application.

    Args:
        video_dir: Directory containing video files
        thumbnails: Dictionary mapping video filenames to thumbnail paths

    Returns:
        Configured Flask application
    """
    # Use package directory for templates
    package_dir = Path(__file__).parent
    app = Flask(__name__, template_folder=str(package_dir / "templates"))

    # Store config
    app.config["VIDEO_DIR"] = video_dir
    app.config["THUMBNAILS"] = thumbnails

    @app.route("/")
    def index():
        """Serve main page with video grid."""
        video_files = sorted(video_dir.glob("*"))
        video_files = [f for f in video_files if f.is_file() and f.name in thumbnails]

        # Build video info list
        videos = []
        for video_file in video_files:
            duration = get_video_duration(video_file)
            videos.append({
                "name": video_file.name,
                "duration": format_duration(duration),
                "has_thumbnail": video_file.name in thumbnails,
            })

        return render_template("index.html", videos=videos)

    @app.route("/video/<path:filename>")
    def stream_video(filename: str):
        """Stream video file with range request support.

        Args:
            filename: Video filename

        Returns:
            Video file response with range support
        """
        video_path = video_dir / filename

        # Security check - ensure file is in video directory
        try:
            video_path = video_path.resolve()
            video_dir_resolved = video_dir.resolve()
            if not str(video_path).startswith(str(video_dir_resolved)):
                abort(403)
        except Exception:
            abort(403)

        if not video_path.exists() or not video_path.is_file():
            abort(404)

        # Get file size
        file_size = video_path.stat().st_size

        # Handle range requests for seeking
        range_header = request.headers.get("Range")
        if range_header:
            byte_start, byte_end = 0, file_size - 1

            # Parse range header
            range_match = range_header.replace("bytes=", "").split("-")
            if range_match[0]:
                byte_start = int(range_match[0])
            if range_match[1]:
                byte_end = int(range_match[1])

            # Ensure valid range
            byte_start = max(0, min(byte_start, file_size - 1))
            byte_end = max(byte_start, min(byte_end, file_size - 1))

            length = byte_end - byte_start + 1

            def generate():
                with open(video_path, "rb") as f:
                    f.seek(byte_start)
                    remaining = length
                    chunk_size = 8192
                    while remaining > 0:
                        chunk = f.read(min(chunk_size, remaining))
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk

            response = Response(
                generate(),
                206,
                mimetype=get_video_mimetype(filename),
                direct_passthrough=True,
            )
            response.headers.add("Content-Range", f"bytes {byte_start}-{byte_end}/{file_size}")
            response.headers.add("Accept-Ranges", "bytes")
            response.headers.add("Content-Length", str(length))
            return response

        # No range request - send entire file
        response = send_file(
            video_path,
            mimetype=get_video_mimetype(filename),
            as_attachment=False,
        )
        response.headers.add("Accept-Ranges", "bytes")
        response.headers.add("Content-Length", str(file_size))
        return response

    @app.route("/thumbnail/<path:filename>")
    def serve_thumbnail(filename: str):
        """Serve thumbnail image for video.

        Args:
            filename: Video filename

        Returns:
            Thumbnail image response
        """
        if filename not in thumbnails:
            abort(404)

        thumbnail_path = thumbnails[filename]
        if not thumbnail_path.exists():
            abort(404)

        return send_file(thumbnail_path, mimetype="image/jpeg")

    return app


# Create module-level app instance for gunicorn
# Config is read from environment variables set by CLI
def _create_app_from_env():
    """Create app instance from environment variables."""
    video_dir_str = os.environ.get("VIDSERVE_VIDEO_DIR")
    thumbnails_json = os.environ.get("VIDSERVE_THUMBNAILS")

    if not video_dir_str or not thumbnails_json:
        raise RuntimeError("VIDSERVE_VIDEO_DIR and VIDSERVE_THUMBNAILS environment variables must be set")

    video_dir = Path(video_dir_str)
    thumbnails = {k: Path(v) for k, v in json.loads(thumbnails_json).items()}

    return create_app(video_dir, thumbnails)


# Module-level app instance for gunicorn
app = _create_app_from_env()

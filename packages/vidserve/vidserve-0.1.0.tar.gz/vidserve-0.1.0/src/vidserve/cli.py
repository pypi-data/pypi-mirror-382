"""Command-line interface for vidserve."""

from pathlib import Path

import click

from vidserve.video_utils import get_video_files, generate_all_thumbnails
from vidserve.server import create_app


@click.command()
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Directory containing video files (default: current directory)",
)
@click.option(
    "--port",
    "-p",
    type=int,
    default=8000,
    help="Port to run server on (default: 8000)",
)
@click.option(
    "--host",
    "-h",
    type=str,
    default="localhost",
    help="Host to bind server to (default: localhost)",
)
def main(directory: Path, port: int, host: str):
    """Serve videos from a directory via web interface.

    Scans the specified directory for video files, generates thumbnails,
    and serves them via a web interface with streaming support.
    """
    print(f"VidServe - Video Server")
    print(f"Scanning directory: {directory.absolute()}")
    print()

    # Scan for video files
    video_files = get_video_files(directory)
    if not video_files:
        print("No video files found in directory!")
        print("Supported formats: .mp4, .avi, .mov, .mkv, .webm, .flv, .wmv, .m4v")
        return

    print(f"Found {len(video_files)} video files")
    print()

    # Generate thumbnails
    thumbnails = generate_all_thumbnails(video_files)
    print()

    # Create and run Flask app
    app = create_app(directory, thumbnails)
    print(f"Starting server at http://{host}:{port}")
    print("Press Ctrl+C to stop")
    print()

    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Command-line interface for the 3D Spacey SDK.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import upload_model, cancel_upload, get_upload_progress, APIError


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="3D Spacey SDK - Upload and manage 3D models",
        prog="spacey3d"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a 3D model")
    upload_parser.add_argument("rar_path", help="Path to the RAR archive")
    upload_parser.add_argument("--title", required=True, help="Model title")
    upload_parser.add_argument("--description", help="Model description")
    upload_parser.add_argument("--tags", nargs="+", help="Model tags")
    upload_parser.add_argument("--links", nargs="+", help="Reference links")
    upload_parser.add_argument("--width", type=float, help="Model width")
    upload_parser.add_argument("--height", type=float, help="Model height")
    upload_parser.add_argument("--length", type=float, help="Model length")
    upload_parser.add_argument("--type", default="3d_model", help="Model type")
    upload_parser.add_argument("--free", action="store_true", help="Mark as free model")
    upload_parser.add_argument("--native-platform", help="Native platform (max, blend, c4d)")
    upload_parser.add_argument("--preview-images", nargs="+", help="Preview image paths")
    upload_parser.add_argument("--background", action="store_true", help="Run in background")
    upload_parser.add_argument("--show-progress", action="store_true", help="Show progress")
    
    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel current upload")
    
    # Progress command
    progress_parser = subparsers.add_parser("progress", help="Check upload progress")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "upload":
            return handle_upload(args)
        elif args.command == "cancel":
            return handle_cancel()
        elif args.command == "progress":
            return handle_progress()
        elif args.command == "version":
            return handle_version()
    except APIError as e:
        print(f"API Error: {e}", file=sys.stderr)
        if e.details:
            print(f"Details: {e.details}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def handle_upload(args) -> int:
    """Handle upload command."""
    # Validate RAR path
    rar_path = Path(args.rar_path)
    if not rar_path.exists():
        print(f"Error: RAR file not found: {rar_path}", file=sys.stderr)
        return 1
    
    # Prepare upload arguments
    upload_kwargs = {
        "rar_path": str(rar_path),
        "title": args.title,
        "description": args.description,
        "tags": args.tags,
        "links": args.links,
        "width": args.width,
        "height": args.height,
        "length": args.length,
        "type": args.type,
        "free": args.free,
        "native_platform": args.native_platform,
        "preview_images": args.preview_images,
        "show_progress": args.show_progress,
        "background": args.background,
    }
    
    # Remove None values
    upload_kwargs = {k: v for k, v in upload_kwargs.items() if v is not None}
    
    print(f"Uploading {rar_path.name}...")
    
    if args.background:
        job = upload_model(**upload_kwargs)
        print(f"Upload started in background. Job ID: {id(job)}")
        print("Use 'spacey3d progress' to check status or 'spacey3d cancel' to cancel.")
    else:
        result = upload_model(**upload_kwargs)
        print("Upload completed successfully!")
        print(f"Result: {result}")
    
    return 0


def handle_cancel() -> int:
    """Handle cancel command."""
    print("Cancelling upload...")
    result = cancel_upload()
    print(f"Cancel result: {result}")
    return 0


def handle_progress() -> int:
    """Handle progress command."""
    pct, status = get_upload_progress()
    if pct is not None:
        print(f"Progress: {pct}%")
    elif status:
        print(f"Status: {status}")
    else:
        print("No upload in progress")
    return 0


def handle_version() -> int:
    """Handle version command."""
    from . import __version__
    print(f"3D Spacey SDK version {__version__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

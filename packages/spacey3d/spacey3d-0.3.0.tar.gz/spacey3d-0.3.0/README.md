# 3D Spacey SDK for Python

A lightweight Python client SDK that provides a simple, easy-to-use interface for uploading 3D models and assets to the 3D Spacey platform. It communicates with the local backend and handles progress tracking, cancellation, and error handling for upload workflows.

## Install

```bash
pip install spacey3d
```

## Basic usage

```python
from spacey3d import upload_model

resp = upload_model(
    rar_path=r"C:\\path\\to\\archive.rar",
    title="My City Block",
    description="Typical city block with shops",
    tags=["city","street","vray"],
    links=["https://reference.site/foo"],
    free=False,
    type="3d_model",
    native_platform="3dsmax",
    preview_images=[r"C:\\path\\to\\cover.jpg"],
    show_progress=True,
)
print(resp)
```

## Background mode

```python
from spacey3d import upload_model

job = upload_model(
    rar_path=r"C:\\path\\to\\archive.rar",
    title="My City Block",
    free=False,
    background=True,
)

for pct, status in job.stream_progress(interval_seconds=1.0):
    if pct is not None:
        print(f"Progress: {pct}%")
    elif status:
        print(status)

print("Final:", job.wait())
```

## Cancel the current upload

```python
from spacey3d import cancel_upload

cancel_upload()
```

## Requirements

- Python 3.8 or higher
- The local 3D Spacey backend must be running at `http://127.0.0.1:9765`
- You must be logged in locally (session is owned by the local backend)
- The `preview_images` argument should be a list of local image file paths

## Features

- **Simple Upload Interface**: Easy-to-use functions for uploading 3D models
- **Progress Tracking**: Real-time progress monitoring with customizable callbacks
- **Background Processing**: Non-blocking uploads with job management
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Platform Support**: Works with 3DS Max, Blender, Cinema 4D, and more
- **Cancellation**: Ability to cancel ongoing uploads

## Development

For development setup:

```bash
git clone https://github.com/3dspacey/spacey3d-python-sdk.git
cd spacey3d-python-sdk
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate
pip install -e .
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

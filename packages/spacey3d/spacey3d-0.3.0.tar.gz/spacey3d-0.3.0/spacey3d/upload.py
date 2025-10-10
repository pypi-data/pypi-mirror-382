import threading
import time
from typing import Any, Callable, Dict, Iterable, Optional, Tuple, Union

from .utils.http import request_json
from .utils.errors import APIError


class UploadJob:
    """Represents an in-flight upload started by `upload_model`."""

    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload
        self._thread: Optional[threading.Thread] = None
        self._done = threading.Event()
        self._result: Optional[Dict[str, Any]] = None
        self._error: Optional[BaseException] = None

    def _run(self) -> None:
        try:
            self._result = _post_upload_request(self._payload)
        except BaseException as exc:
            self._error = exc
        finally:
            self._done.set()

    def start(self) -> "UploadJob":
        if self._thread is not None:
            return self
        self._thread = threading.Thread(target=self._run, name="spacey-upload", daemon=True)
        self._thread.start()
        return self

    def wait(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        self._done.wait(timeout)
        if not self._done.is_set():
            raise TimeoutError("Upload still in progress")
        if self._error:
            raise self._error
        assert self._result is not None
        return self._result

    def is_done(self) -> bool:
        return self._done.is_set()

    def cancel(self) -> Dict[str, Any]:
        return cancel_upload()

    def progress_once(self) -> Tuple[Optional[int], Optional[str]]:
        return get_upload_progress()

    def stream_progress(self, interval_seconds: float = 1.0) -> Iterable[Tuple[Optional[int], Optional[str]]]:
        while not self.is_done():
            yield self.progress_once()
            time.sleep(interval_seconds)


def _clean_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in payload.items() if v is not None}


def _normalize_free_flag(free: Union[bool, int]) -> int:
    if isinstance(free, bool):
        return 1 if free else 0
    return 1 if free == 1 else 0


def _normalize_native_platform(native: Optional[Union[str, int]]) -> Optional[str]:
    if native is None:
        return None
    if isinstance(native, int):
        native_map = {1: "max", 2: "c4d", 3: "blend"}
        return native_map.get(native)

    native_str = str(native).strip().lower()
    aliases = {
        "3dsmax": "max",
        "3ds max": "max",
        "max": "max",
        "blender": "blend",
        "blend": "blend",
        "c4d": "c4d",
        "cinema4d": "c4d",
    }
    return aliases.get(native_str, native_str)


def _coerce_int(value: Optional[Union[int, float, str]]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def upload_model(
    *,
    rar_path: str,
    title: str,
    description: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    links: Optional[Iterable[str]] = None,
    width: Optional[Union[int, float]] = None,
    height: Optional[Union[int, float]] = None,
    length: Optional[Union[int, float]] = None,
    type: str = "3d_model",
    free: bool = False,
    native_platform: Optional[str] = None,
    preview_images: Optional[Iterable[str]] = None,
    show_progress: bool = False,
    on_progress: Optional[Callable[[Optional[int], Optional[str]], None]] = None,
    background: bool = False,
) -> Union[Dict[str, Any], UploadJob]:
    """
    Start an upload. If background=False, waits and returns the final response.
    If background=True, returns an UploadJob immediately.
    """
    native = _normalize_native_platform(native_platform) if native_platform else None
    width = _coerce_int(width)
    height = _coerce_int(height)
    length = _coerce_int(length)
    payload: Dict[str, Any] = {
        "rar_path": rar_path,
        "title": title,
        "description": description,
        "tags": list(tags) if tags else [],
        "links": list(links) if links else [],
        "width": width,
        "height": height,
        "length": length,
        "type": type,
        "free": _normalize_free_flag(free),
        "native_platform": native,
        # backend expects this exact key
        "perview_imgs": list(preview_images) if preview_images else [],
    }
    payload = _clean_payload(payload)

    job = UploadJob(payload).start()
    if background:
        return job

    if show_progress or on_progress:
        last: Optional[Tuple[Optional[int], Optional[str]]] = None
        while not job.is_done():
            prog = get_upload_progress()
            if prog != last:
                if on_progress:
                    on_progress(*prog)
                elif show_progress:
                    pct, status = prog
                    if isinstance(pct, int):
                        print(f"[Upload] {pct}%")
                    elif status:
                        print(f"[Upload] {status}")
                last = prog
            time.sleep(1.0)

    return job.wait()


def cancel_upload() -> Dict[str, Any]:
    return request_json("GET", "/api/upload/upload_cancel")


def get_upload_progress() -> Tuple[Optional[int], Optional[str]]:
    try:
        data = request_json("GET", "/api/upload/upload_progress")
        details = data.get("data", {}).get("details")
    except APIError as e:
        return None, f"error: {str(e)}"

    if isinstance(details, (int, float)):
        return int(details), None

    if isinstance(details, str):
        status_map = {
            "upload_is_preparing": "preparing",
            "taying_again_on_falier": "retrying",
            "upload_cancel": "cancelled",
            "error_uploading": "error",
            "upload_completed_done": "completed",
        }
        return None, status_map.get(details, details)

    return None, None


def _post_upload_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    return request_json("POST", "/api/upload/upload_request", json=payload)





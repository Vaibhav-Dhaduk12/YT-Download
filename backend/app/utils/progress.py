from typing import Callable, Optional


def make_progress_hook(
    on_progress: Optional[Callable[[float], None]] = None,
    on_complete: Optional[Callable[[], None]] = None,
) -> Callable[[dict], None]:
    def hook(d: dict) -> None:
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total and on_progress:
                progress = (downloaded / total) * 100
                on_progress(round(progress, 1))
        elif status == "finished" and on_complete:
            on_complete()

    return hook

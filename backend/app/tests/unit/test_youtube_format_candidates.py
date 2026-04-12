import pytest

from app.api.exceptions.custom import DownloadError
from app.core.youtube import YouTubeAdapter


@pytest.fixture
def adapter():
    return YouTubeAdapter()


# ---------------------------------------------------------------------------
# format_id provided – ffmpeg available
# ---------------------------------------------------------------------------


def test_format_id_ffmpeg_first_candidate_merges_audio(adapter):
    """When a format_id is given and ffmpeg is available the first candidate
    must request a merge so that video-only formats (e.g. 137) are muxed with
    the best available audio track."""
    candidates = adapter._build_format_candidates(
        format_id="137", quality="best", audio_only=False, ffmpeg_available=True
    )
    assert "+bestaudio[ext=m4a]" in candidates[0], (
        "First candidate must force audio merge, got: " + candidates[0]
    )
    assert candidates[0] == "137+bestaudio[ext=m4a]/bestaudio/best"


def test_format_id_ffmpeg_fallback_candidates_present(adapter):
    """When the merged candidate fails, best-merge and best fallbacks should
    be included."""
    candidates = adapter._build_format_candidates(
        format_id="248", quality="best", audio_only=False, ffmpeg_available=True
    )
    assert "bestvideo+bestaudio[ext=m4a]/bestaudio/best" in candidates
    assert "best" in candidates


def test_format_id_ffmpeg_no_duplicates(adapter):
    candidates = adapter._build_format_candidates(
        format_id="137", quality="best", audio_only=False, ffmpeg_available=True
    )
    assert len(candidates) == len(set(candidates))


# ---------------------------------------------------------------------------
# format_id provided – ffmpeg NOT available
# ---------------------------------------------------------------------------


def test_format_id_no_ffmpeg_uses_progressive_format(adapter):
    """Without ffmpeg we cannot mux, so we must fall back to progressive
    formats that already carry audio (acodec!=none) and must not use
    the bare video-only format_id."""
    candidates = adapter._build_format_candidates(
        format_id="137", quality="best", audio_only=False, ffmpeg_available=False
    )
    # All candidates must require audio track (no video-only streams).
    assert all(("acodec!=none" in c) or ("acodec^=mp4a" in c) for c in candidates), (
        "All candidates must require audio when ffmpeg is unavailable"
    )
    # The bare video-only format_id must not appear on its own in any candidate.
    assert all("137" not in c for c in candidates), (
        "Bare video-only format_id must not be used when ffmpeg is unavailable"
    )


# ---------------------------------------------------------------------------
# audio_only – unchanged behaviour
# ---------------------------------------------------------------------------


def test_audio_only_ffmpeg_uses_bestaudio(adapter):
    candidates = adapter._build_format_candidates(
        format_id=None, quality="best", audio_only=True, ffmpeg_available=True
    )
    assert candidates[0].startswith("bestaudio")


def test_audio_only_no_ffmpeg_avoids_merge(adapter):
    candidates = adapter._build_format_candidates(
        format_id=None, quality="best", audio_only=True, ffmpeg_available=False
    )
    # Should not contain a '+' merge operator
    assert all("+" not in c for c in candidates)


# ---------------------------------------------------------------------------
# quality-based (no format_id) – unchanged behaviour
# ---------------------------------------------------------------------------


def test_quality_best_ffmpeg(adapter):
    candidates = adapter._build_format_candidates(
        format_id=None, quality="best", audio_only=False, ffmpeg_available=True
    )
    assert "bestvideo+bestaudio[ext=m4a]/bestaudio/best" in candidates


def test_quality_worst_ffmpeg(adapter):
    candidates = adapter._build_format_candidates(
        format_id=None, quality="worst", audio_only=False, ffmpeg_available=True
    )
    assert "worstvideo+worstaudio[ext=m4a]/worstaudio/worst" in candidates


def test_quality_height_ffmpeg(adapter):
    candidates = adapter._build_format_candidates(
        format_id=None, quality="720", audio_only=False, ffmpeg_available=True
    )
    assert any("720" in c for c in candidates)


def test_format_id_without_ffmpeg_fails_fast(adapter, monkeypatch, tmp_path):
    monkeypatch.setattr("app.core.youtube.settings.temp_dir", str(tmp_path))
    monkeypatch.setattr(adapter, "_has_ffmpeg", lambda: False)

    with pytest.raises(DownloadError) as exc:
        adapter._do_download(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            format_id="137",
            quality="best",
            audio_only=False,
            progress_hook=None,
            output_suffix="unit-test",
        )

    error_text = str(exc.value)
    assert "FFmpeg + FFprobe" in error_text
    assert "winget install Gyan.FFmpeg" in error_text


def test_validate_output_rejects_video_without_audio(adapter, monkeypatch):
    monkeypatch.setattr("app.core.youtube.os.path.exists", lambda _: True)
    monkeypatch.setattr("app.core.youtube.os.path.getsize", lambda _: 250 * 1024)
    monkeypatch.setattr(
        "app.core.youtube.shutil.which",
        lambda command: "ffprobe" if command == "ffprobe" else None,
    )

    class Result:
        returncode = 0
        stdout = "codec_type=video\n"
        stderr = ""

    monkeypatch.setattr("app.core.youtube.subprocess.run", lambda *args, **kwargs: Result())

    is_valid, error_msg = adapter._validate_output_file(
        "fake.mp4",
        require_video_stream=True,
        require_audio_stream=True,
    )
    assert is_valid is False
    assert "audio" in error_msg.lower()

import pytest

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
    assert "+bestaudio" in candidates[0], (
        "First candidate must force audio merge, got: " + candidates[0]
    )
    assert candidates[0] == "137+bestaudio/best"


def test_format_id_ffmpeg_fallback_candidates_present(adapter):
    """When the merged candidate fails, best-merge and best fallbacks should
    be included."""
    candidates = adapter._build_format_candidates(
        format_id="248", quality="best", audio_only=False, ffmpeg_available=True
    )
    assert "bestvideo+bestaudio/best" in candidates
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
    assert all("acodec!=none" in c for c in candidates), (
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
    assert "bestvideo+bestaudio/best" in candidates


def test_quality_worst_ffmpeg(adapter):
    candidates = adapter._build_format_candidates(
        format_id=None, quality="worst", audio_only=False, ffmpeg_available=True
    )
    assert "worstvideo+worstaudio/worst" in candidates


def test_quality_height_ffmpeg(adapter):
    candidates = adapter._build_format_candidates(
        format_id=None, quality="720", audio_only=False, ffmpeg_available=True
    )
    assert any("720" in c for c in candidates)

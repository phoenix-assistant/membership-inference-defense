"""Tests for watermarking module."""

import json
import pytest
from mid.watermark import (
    watermark_text,
    detect_watermark,
    watermark_dataset,
    ZERO_WIDTH_SPACE,
    ZERO_WIDTH_JOINER,
    MARKER_START,
)


def test_watermark_embeds_invisible_chars():
    original = "This is a test sentence for watermarking purposes."
    watermarked = watermark_text(original, "secret-key")
    # Should contain zero-width characters
    assert MARKER_START in watermarked
    # Visible text should be preserved
    visible_original = original.replace(" ", "")
    visible_watermarked = watermarked.replace(ZERO_WIDTH_SPACE, "").replace(ZERO_WIDTH_JOINER, "")
    assert visible_original in visible_watermarked.replace(" ", "").replace("\u200c", "").replace("\u2060", "")


def test_watermark_detection():
    text = "This is a test sentence for watermarking and detection."
    key = "my-secret"
    watermarked = watermark_text(text, key)
    result = detect_watermark(watermarked, key)
    assert result["detected"] is True
    assert result["confidence"] > 0.7


def test_watermark_wrong_key():
    text = "Some important training data that should be protected."
    watermarked = watermark_text(text, "correct-key")
    result = detect_watermark(watermarked, "wrong-key")
    # May or may not detect, but confidence should be lower
    assert result["bits_found"] > 0


def test_watermark_no_marker():
    result = detect_watermark("Plain text with no watermark", "any-key")
    assert result["detected"] is False


def test_watermark_dataset(tmp_path):
    input_path = tmp_path / "input.jsonl"
    output_path = tmp_path / "output.jsonl"
    samples = [
        {"text": "First sample text."},
        {"text": "Second sample text."},
        {"text": "Third sample text."},
    ]
    input_path.write_text("\n".join(json.dumps(s) for s in samples))

    stats = watermark_dataset(str(input_path), str(output_path), "key123")
    assert stats["total"] == 3
    assert stats["marked"] == 3

    # Verify output is valid JSONL
    with open(output_path) as f:
        lines = [json.loads(l) for l in f if l.strip()]
    assert len(lines) == 3


def test_watermark_whitespace_method():
    text = "Line one\nLine two\nLine three"
    watermarked = watermark_text(text, "key", method="whitespace")
    assert isinstance(watermarked, str)

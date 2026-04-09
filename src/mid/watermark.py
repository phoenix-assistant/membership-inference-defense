"""Data watermarking — embed invisible markers in training data for IP tracking."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


# Zero-width Unicode characters for steganography
ZERO_WIDTH_SPACE = "\u200b"
ZERO_WIDTH_JOINER = "\u200d"
ZERO_WIDTH_NON_JOINER = "\u200c"
WORD_JOINER = "\u2060"

BIT_CHARS = {0: ZERO_WIDTH_SPACE, 1: ZERO_WIDTH_JOINER}
MARKER_START = ZERO_WIDTH_NON_JOINER
MARKER_END = WORD_JOINER


def _key_to_seed(key: str) -> int:
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)


def _generate_watermark_bits(text: str, key: str, length: int = 32) -> list[int]:
    """Generate deterministic watermark bits from text + key."""
    mac = hmac.new(key.encode(), text.encode(), hashlib.sha256).hexdigest()
    bits = []
    for char in mac:
        val = int(char, 16)
        bits.extend([(val >> i) & 1 for i in range(4)])
        if len(bits) >= length:
            break
    return bits[:length]


def _embed_unicode(text: str, bits: list[int]) -> str:
    """Embed bits as zero-width Unicode characters into text."""
    encoded = MARKER_START
    for b in bits:
        encoded += BIT_CHARS[b]
    encoded += MARKER_END

    # Insert at a deterministic position (after first sentence or mid-text)
    mid = len(text) // 2
    # Find nearest space
    insert_pos = text.find(" ", mid)
    if insert_pos == -1:
        insert_pos = mid

    return text[:insert_pos] + encoded + text[insert_pos:]


def _embed_whitespace(text: str, bits: list[int]) -> str:
    """Embed bits using trailing whitespace patterns."""
    lines = text.split("\n")
    for i, bit in enumerate(bits):
        if i < len(lines):
            lines[i] = lines[i].rstrip() + (" " if bit else "")
    return "\n".join(lines)


def watermark_text(text: str, key: str, method: str = "unicode") -> str:
    """Embed invisible watermark into a single text sample."""
    bits = _generate_watermark_bits(text, key)

    if method == "unicode":
        return _embed_unicode(text, bits)
    elif method == "whitespace":
        return _embed_whitespace(text, bits)
    elif method == "synonym":
        # Synonym substitution is a placeholder — would need NLP pipeline
        return _embed_unicode(text, bits)
    else:
        raise ValueError(f"Unknown watermark method: {method}")


def detect_watermark(text: str, key: str) -> dict[str, Any]:
    """Detect if a watermark is present in text."""
    # Look for zero-width marker
    start_idx = text.find(MARKER_START)
    end_idx = text.find(MARKER_END)

    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return {"detected": False, "confidence": 0.0, "bits_found": 0}

    marker_content = text[start_idx + 1:end_idx]
    extracted_bits = []
    for ch in marker_content:
        if ch == BIT_CHARS[0]:
            extracted_bits.append(0)
        elif ch == BIT_CHARS[1]:
            extracted_bits.append(1)

    # Strip watermark to get original text for verification
    clean = text[:start_idx] + text[end_idx + 1:]
    expected_bits = _generate_watermark_bits(clean, key)

    # Compare
    match_count = sum(1 for a, b in zip(extracted_bits, expected_bits) if a == b)
    total = min(len(extracted_bits), len(expected_bits))
    confidence = match_count / total if total > 0 else 0.0

    return {
        "detected": confidence > 0.7,
        "confidence": round(confidence, 4),
        "bits_found": len(extracted_bits),
        "bits_matched": match_count,
    }


def watermark_dataset(input_path: str, output_path: str, key: str, method: str = "unicode") -> dict[str, int]:
    """Watermark all samples in a JSONL dataset."""
    total = 0
    marked = 0

    with open(input_path) as fin, open(output_path, "w") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            total += 1
            record = json.loads(line)
            text = record.get("text", "")
            if text:
                record["text"] = watermark_text(text, key, method=method)
                marked += 1
            fout.write(json.dumps(record) + "\n")

    return {"total": total, "marked": marked, "method": method}

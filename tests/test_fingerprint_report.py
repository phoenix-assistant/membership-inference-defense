"""Tests for fingerprinting and report generation."""

import json
import pytest
from mid.fingerprint import generate_fingerprint, compare_fingerprints
from mid.report import generate_report


def test_fingerprint_generation():
    fp = generate_fingerprint("test-model")
    assert "fingerprint_hash" in fp
    assert fp["num_probes"] == 16
    assert "summary" in fp


def test_fingerprint_deterministic():
    fp1 = generate_fingerprint("model-x")
    fp2 = generate_fingerprint("model-x")
    assert fp1["fingerprint_hash"] == fp2["fingerprint_hash"]


def test_fingerprint_different_models():
    fp1 = generate_fingerprint("model-a")
    fp2 = generate_fingerprint("model-b")
    assert fp1["fingerprint_hash"] != fp2["fingerprint_hash"]


def test_compare_fingerprints():
    fp1 = generate_fingerprint("same-model")
    fp2 = generate_fingerprint("same-model")
    result = compare_fingerprints(fp1, fp2)
    assert result["hash_match"] is True
    assert result["likely_same_model"] is True


def test_report_json(tmp_path):
    evidence = {
        "model": "test",
        "attack_type": "confidence",
        "threshold": 0.8,
        "summary": {"total_samples": 2, "members_detected": 1, "avg_confidence": 0.75},
        "samples": [
            {"text": "hello", "score": 0.9, "is_member": True},
            {"text": "world", "score": 0.3, "is_member": False},
        ],
    }
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(evidence))
    output = tmp_path / "report.json"
    generate_report(str(evidence_path), str(output), fmt="json")
    report = json.loads(output.read_text())
    assert report["tool"] == "membership-inference-defense"


def test_report_html(tmp_path):
    evidence = {
        "model": "test",
        "attack_type": "shadow",
        "threshold": 0.8,
        "summary": {"total_samples": 1, "members_detected": 0, "avg_confidence": 0.3},
        "samples": [{"text": "test", "score": 0.3, "is_member": False}],
    }
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(evidence))
    output = tmp_path / "report.html"
    generate_report(str(evidence_path), str(output), fmt="html")
    html = output.read_text()
    assert "<html" in html
    assert "MID Forensic Report" in html

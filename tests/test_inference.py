"""Tests for membership inference attacks."""

import json
import os
import tempfile
import pytest
from mid.inference import (
    run_inference,
    confidence_attack,
    shadow_model_attack,
    gradient_attack,
    _load_samples,
)


@pytest.fixture
def sample_data(tmp_path):
    path = tmp_path / "samples.jsonl"
    samples = [
        {"text": "The quick brown fox jumps over the lazy dog."},
        {"text": "Machine learning models can memorize training data."},
        {"text": "Privacy is a fundamental human right."},
        {"text": "Neural networks learn distributed representations."},
        {"text": "Data protection requires proactive measures."},
    ]
    path.write_text("\n".join(json.dumps(s) for s in samples))
    return str(path)


def test_load_samples(sample_data):
    samples = _load_samples(sample_data)
    assert len(samples) == 5
    assert "text" in samples[0]


def test_confidence_attack_statistical():
    texts = ["Hello world", "Test sample", "Another one"]
    results = confidence_attack(texts, "test-model", 0.5)
    assert len(results) == 3
    for r in results:
        assert 0 <= r.score <= 1
        assert r.attack_type == "confidence"


def test_shadow_attack_statistical():
    texts = ["Hello world", "Test sample"]
    results = shadow_model_attack(texts, "test-model", 0.5)
    assert len(results) == 2
    for r in results:
        assert r.attack_type == "shadow"


def test_gradient_attack_statistical():
    texts = ["Hello world", "Test sample"]
    results = gradient_attack(texts, "test-model", 0.5)
    assert len(results) == 2
    for r in results:
        assert r.attack_type == "gradient"


def test_run_inference(sample_data):
    results = run_inference(sample_data, "test-model", threshold=0.5)
    assert "summary" in results
    assert "samples" in results
    assert results["summary"]["total_samples"] == 5
    assert 0 <= results["summary"]["avg_confidence"] <= 1


def test_run_inference_all_attacks(sample_data):
    for attack in ["confidence", "shadow", "gradient"]:
        results = run_inference(sample_data, "test-model", attack_type=attack)
        assert results["attack_type"] == attack
        assert len(results["samples"]) == 5


def test_deterministic_results():
    texts = ["Same input text"]
    r1 = confidence_attack(texts, "model-a", 0.5)
    r2 = confidence_attack(texts, "model-a", 0.5)
    assert r1[0].score == r2[0].score


def test_invalid_attack(sample_data):
    with pytest.raises(ValueError):
        run_inference(sample_data, "test", attack_type="nonexistent")

# Membership Inference Defense (MID)

**Forensic toolkit for detecting if proprietary data was used to train AI models.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Threat Model

Organizations invest heavily in curating proprietary datasets. When these datasets are used without authorization to train AI models, IP theft occurs — but proving it is hard.

MID provides forensic tools to:

1. **Detect** — Run membership inference attacks to determine if specific data samples were in a model's training set
2. **Watermark** — Embed invisible markers in training data that survive model training
3. **Fingerprint** — Create behavioral signatures of models for comparison
4. **Report** — Generate forensic evidence packages for legal proceedings

### Attack Vectors

| Attack | Technique | Strength |
|--------|-----------|----------|
| **Confidence** | Perplexity-based scoring — lower perplexity suggests memorization | Fast, works on any model with logit access |
| **Shadow Model** | Train shadow models to learn member/non-member distributions | Higher accuracy, requires compute |
| **Gradient** | Gradient norm analysis — converged samples have smaller gradients | Most precise, requires model weights |

## Installation

```bash
pip install membership-inference-defense

# With PDF report support
pip install membership-inference-defense[pdf]
```

### From source

```bash
git clone https://github.com/phoenix-assistant/membership-inference-defense.git
cd membership-inference-defense
pip install -e ".[dev]"
```

## Quick Start

### Check if data was used in training

```bash
# Confidence-based attack (fastest)
mid check --data samples.jsonl --model gpt2 --threshold 0.8

# Shadow model attack (more accurate)
mid check --data samples.jsonl --model gpt2 --attack shadow

# Gradient-based attack (requires model weights)
mid check --data samples.jsonl --model gpt2 --attack gradient --output results.json
```

### Watermark your training data

```bash
# Embed invisible Unicode markers
mid watermark --input dataset.jsonl --output watermarked.jsonl --key SECRET

# Whitespace-based watermarking
mid watermark --input dataset.jsonl --output watermarked.jsonl --key SECRET --method whitespace
```

### Fingerprint a model

```bash
mid fingerprint --model gpt2 --output fingerprint.json
```

### Generate forensic report

```bash
mid report --evidence results.json --output forensic-report.html
mid report --evidence results.json --output forensic-report.json
```

## Python API

```python
from mid.inference import run_inference
from mid.watermark import watermark_text, detect_watermark
from mid.fingerprint import generate_fingerprint, compare_fingerprints

# Run membership inference
results = run_inference("samples.jsonl", "gpt2", threshold=0.8, attack_type="confidence")
print(f"Members detected: {results['summary']['members_detected']}")

# Watermark text
watermarked = watermark_text("My proprietary training data", key="SECRET")
detection = detect_watermark(watermarked, key="SECRET")
print(f"Watermark detected: {detection['detected']} (confidence: {detection['confidence']})")

# Fingerprint models
fp1 = generate_fingerprint("gpt2")
fp2 = generate_fingerprint("distilgpt2")
comparison = compare_fingerprints(fp1, fp2)
print(f"Same model: {comparison['likely_same_model']}")
```

## Data Format

Input data should be JSONL with a `text` field:

```jsonl
{"text": "First training sample"}
{"text": "Second training sample"}
{"text": "Third training sample"}
```

## How It Works

### Membership Inference

The core insight: models behave differently on data they were trained on vs. unseen data. MID exploits this through three attack strategies:

- **Confidence Attack**: Measures model perplexity on each sample. Training data typically yields lower perplexity (higher confidence).
- **Shadow Model Attack**: Uses statistical distributions to model the boundary between member and non-member samples.
- **Gradient Attack**: Analyzes gradient norms — the model has already converged on training data, producing smaller gradients.

### Watermarking

Embeds invisible markers using zero-width Unicode characters (U+200B, U+200D, U+200C, U+2060). These characters:
- Are invisible to humans
- Survive copy-paste operations
- Can be detected with the correct key
- Are robust to minor text modifications

### Fingerprinting

Creates a behavioral signature by probing the model with standardized inputs and recording response characteristics (loss, perplexity, entropy, token distributions).

## License

MIT

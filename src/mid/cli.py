"""CLI entry point for membership-inference-defense."""

import json
import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(package_name="membership-inference-defense")
def cli():
    """MID — Membership Inference Defense forensic toolkit."""
    pass


@cli.command()
@click.option("--data", required=True, help="Path to data samples (JSONL)")
@click.option("--model", required=True, help="Target model name or path")
@click.option("--threshold", default=0.8, type=float, help="Membership threshold (0-1)")
@click.option("--attack", default="confidence", type=click.Choice(["confidence", "shadow", "gradient"]))
@click.option("--output", default=None, help="Output JSON path")
def check(data, model, threshold, attack, output):
    """Check if data samples were used in model training."""
    from mid.inference import run_inference

    results = run_inference(data, model, threshold=threshold, attack_type=attack)

    if output:
        with open(output, "w") as f:
            json.dump(results, f, indent=2)
        console.print(f"[green]Results written to {output}[/green]")
    else:
        members = sum(1 for r in results["samples"] if r["is_member"])
        total = len(results["samples"])
        console.print(f"[bold]Membership Inference Results[/bold]")
        console.print(f"  Attack: {attack}")
        console.print(f"  Threshold: {threshold}")
        console.print(f"  Members detected: {members}/{total}")
        console.print(f"  Confidence (avg): {results['summary']['avg_confidence']:.3f}")


@cli.command()
@click.option("--input", "input_path", required=True, help="Input dataset (JSONL)")
@click.option("--output", required=True, help="Output watermarked dataset (JSONL)")
@click.option("--key", required=True, help="Secret watermark key")
@click.option("--method", default="unicode", type=click.Choice(["unicode", "synonym", "whitespace"]))
def watermark(input_path, output, key, method):
    """Embed invisible watermarks in training data."""
    from mid.watermark import watermark_dataset

    stats = watermark_dataset(input_path, output, key, method=method)
    console.print(f"[green]Watermarked {stats['total']} samples → {output}[/green]")
    console.print(f"  Method: {method}")
    console.print(f"  Markers embedded: {stats['marked']}")


@cli.command()
@click.option("--model", required=True, help="Model name or path")
@click.option("--output", default=None, help="Output fingerprint JSON path")
def fingerprint(model, output):
    """Generate a behavioral fingerprint of a model."""
    from mid.fingerprint import generate_fingerprint

    fp = generate_fingerprint(model)

    if output:
        with open(output, "w") as f:
            json.dump(fp, f, indent=2)
        console.print(f"[green]Fingerprint written to {output}[/green]")
    else:
        console.print(f"[bold]Model Fingerprint[/bold]")
        console.print(f"  Model: {fp['model']}")
        console.print(f"  Hash: {fp['fingerprint_hash']}")
        console.print(f"  Probes: {fp['num_probes']}")


@cli.command()
@click.option("--evidence", required=True, help="Evidence JSON file")
@click.option("--output", required=True, help="Output report path (.json, .html)")
@click.option("--format", "fmt", default=None, type=click.Choice(["json", "html"]))
def report(evidence, output, fmt):
    """Generate forensic evidence report."""
    from mid.report import generate_report

    if fmt is None:
        if output.endswith(".html"):
            fmt = "html"
        else:
            fmt = "json"

    generate_report(evidence, output, fmt=fmt)
    console.print(f"[green]Report generated → {output}[/green]")


if __name__ == "__main__":
    cli()

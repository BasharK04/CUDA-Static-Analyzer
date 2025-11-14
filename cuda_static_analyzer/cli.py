"""CLI entry point using Typer."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .analyzer import Analyzer
from .rules import registry

app = typer.Typer(help="CUDA Security Static Analyzer")
console = Console()


@app.command()
def scan(
    path: Path = typer.Argument(..., help="CUDA source file or directory to scan"),
    sarif_out: Optional[Path] = typer.Option(None, help="Optional SARIF output location"),
) -> None:
    """Run the analyzer against the supplied path."""

    source_paths = _collect_sources(path)
    if not source_paths:
        typer.secho("No .cu sources discovered", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    analyzer = Analyzer()
    result = analyzer.scan(source_paths)

    _render_findings(result.findings)
    console.print("\n[bold]Metrics[/bold]")
    for key, value in result.metrics.items():
        console.print(f" - {key}: {value}")

    if sarif_out is not None:
        sarif_out.parent.mkdir(parents=True, exist_ok=True)
        sarif_out.write_text(json.dumps(result.sarif, indent=2))
        console.print(f"\nSARIF report written to {sarif_out}")


@app.command()
def rules() -> None:
    """List registered rules and descriptions."""

    table = Table(title="Registered CUDA security rules")
    table.add_column("Rule ID")
    table.add_column("Severity")
    table.add_column("Description")

    for rule in registry.rules:
        table.add_row(rule.id, getattr(rule, "severity", "n/a"), getattr(rule, "description", ""))

    console.print(table)


def _collect_sources(path: Path):
    if path.is_file() and path.suffix == ".cu":
        return [path]
    if path.is_dir():
        return sorted(sub_path for sub_path in path.rglob("*.cu"))
    return []


def _render_findings(findings):
    if not findings:
        console.print("\n[green]No issues detected[/green]")
        return

    table = Table(title="Security findings")
    table.add_column("Rule")
    table.add_column("Severity")
    table.add_column("Location")
    table.add_column("Message")
    table.add_column("Exploit Prob.")

    for finding in findings:
        metadata = finding.metadata or {}
        location = f"{finding.location.path}:{finding.location.line}"
        probability = metadata.get("exploit_probability", 0)
        table.add_row(
            finding.rule_id,
            finding.severity,
            location,
            finding.message,
            f"{probability:.2f}",
        )
    console.print(table)


if __name__ == "__main__":  # pragma: no cover
    app()

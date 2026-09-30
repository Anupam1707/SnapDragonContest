"""
GuardianEdge Command Line Interface.
Run local DLP scans, benchmark hardware, or launch background monitoring daemon.
"""

import argparse
import sys
import uvicorn
from rich.console import Console
from rich.table import Table

from guardian_edge.detector import detector
from guardian_edge.redactor import redactor
from guardian_edge.npu_engine import npu_engine
from benchmarks.benchmark_suite import run_comparative_benchmark

console = Console()

def cli_scan(text: str):
    console.print(f"[bold cyan]GuardianEdge Scanning Payload on Snapdragon Hexagon NPU...[/bold cyan]")
    entities, telemetry = detector.scan_text(text)
    redacted, count = redactor.redact_text(text, entities)

    console.print(f"\n[bold green]Scan Complete:[/bold green] {count} sensitive entities neutralized.")
    console.print(f"[yellow]Inference Latency:[/yellow] {telemetry['latency_ms']} ms")
    console.print(f"[yellow]Energy Saved vs CPU:[/yellow] {telemetry['energy_saved_percent']} %")

    if entities:
        table = Table(title="Detected Entities")
        table.add_column("Category", style="cyan")
        table.add_column("Severity", style="red")
        table.add_column("Preview", style="magenta")
        table.add_column("Confidence", style="green")

        for e in entities:
            table.add_row(e.category, e.severity, e.value[:14] + "...", f"{e.confidence*100:.1f}%")
        console.print(table)

    console.print("\n[bold]Neutralized Safe Text:[/bold]")
    console.print(redacted)

def main():
    parser = argparse.ArgumentParser(description="GuardianEdge - Snapdragon X Hexagon NPU DLP")
    subparsers = parser.add_subparsers(dest="command")

    # Scan command
    scan_p = subparsers.add_parser("scan", help="Scan text string for sensitive data")
    scan_p.add_argument("text", type=str, help="Text to scan")

    # Serve command
    serve_p = subparsers.add_parser("serve", help="Launch interactive web dashboard & API")
    serve_p.add_argument("--port", type=int, default=8844, help="Port to run server on")
    serve_p.add_argument("--host", type=str, default="127.0.0.1", help="Host address")

    # Benchmark command
    subparsers.add_parser("benchmark", help="Run comparative Snapdragon X NPU benchmarks")

    args = parser.parse_args()

    if args.command == "scan":
        cli_scan(args.text)
    elif args.command == "serve":
        console.print(f"[bold red]Starting GuardianEdge Dashboard on http://{args.host}:{args.port}[/bold red]")
        uvicorn.run("guardian_edge.server:app", host=args.host, port=args.port, reload=False)
    elif args.command == "benchmark":
        results = run_comparative_benchmark()
        console.print_json(data=results)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

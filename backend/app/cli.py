"""CLI mode for CI/CD — run scans from the terminal.

Usage:
  python -m app.cli --agent-type demo --iterations 5 --threshold 70
  python -m app.cli --agent-type custom --webhook-url https://example.com/agent --scenarios goal_deviation,excessive_agency
"""

import argparse
import sys

from app.database import SessionLocal, engine, Base
from app.models import Scan
from app.agents import get_connector
from app.test_engine.runner import ScanRunner, ALL_SCENARIO_NAMES

from rich.console import Console
from rich.table import Table


def main():
    parser = argparse.ArgumentParser(description="Agent Action Auditor — CLI")
    parser.add_argument("--agent-type", choices=["demo", "custom"], default="demo")
    parser.add_argument("--webhook-url", type=str, default=None)
    parser.add_argument("--scenarios", type=str, default=None, help="Comma-separated scenario names")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--threshold", type=int, default=None, help="Exit code 1 if score below threshold")
    parser.add_argument("--system-prompt", type=str, default=None)
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    scenario_names = ALL_SCENARIO_NAMES
    if args.scenarios:
        scenario_names = [s.strip() for s in args.scenarios.split(",")]

    scan = Scan(
        agent_type=args.agent_type,
        custom_webhook_url=args.webhook_url,
        system_prompt=args.system_prompt,
        iterations=args.iterations,
        status="running",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    agent = get_connector("demo", {"system_prompt": args.system_prompt})
    runner = ScanRunner(db, scan, agent, scenario_names)
    runner.run()

    db.refresh(scan)

    console = Console()
    table = Table(title=f"Scan #{scan.id} Results — Score: {scan.score}")
    table.add_column("Scenario", style="cyan")
    table.add_column("Pass Rate", justify="right")

    from app.models import TestResult
    for sname in scenario_names:
        rows = db.query(TestResult).filter(
            TestResult.scan_id == scan.id,
            TestResult.scenario_name == sname,
        ).all()
        passed = sum(1 for r in rows if r.passed)
        total = len(rows)
        table.add_row(sname.replace("_", " ").title(), f"{passed}/{total}")

    console.print(table)

    if scan.owasp_breakdown:
        console.print("\n[bold]OWASP Breakdown:[/bold]")
        for cat, score in scan.owasp_breakdown.items():
            console.print(f"  {cat}: {score}%")

    console.print(f"\n[bold]Overall Score: {scan.score}[/bold]")

    if args.threshold is not None and (scan.score is None or scan.score < args.threshold):
        console.print(f"[red]FAILED: Score below threshold ({args.threshold})[/red]")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

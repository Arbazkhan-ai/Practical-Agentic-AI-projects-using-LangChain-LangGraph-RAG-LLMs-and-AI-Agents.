"""
Main CLI entry point to run the Market Intelligence Research Agent.
"""

import os
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure app directory is in path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from graph import research_graph

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None


def print_msg(msg: str, style: str = ""):
    if HAS_RICH and console:
        console.print(msg)
    else:
        # Clean rich tags if rich is not present
        import re
        clean = re.sub(r"\[/?\w+.*?\]", "", msg)
        print(clean)


SAMPLE_BRIEF = {
    "title": "Food & Tourism: Capturing Value from Farm-to-Table Experiences",
    "objective": "Evaluate the economic feasibility, supply chain linkages, and local value capture of farm-to-table initiatives in Caribbean tourism economies to support sustainable investment decisions.",
    "questions": """What is the scale of food import dependency in the hotel and restaurant sector across key Caribbean markets?
What are the primary supply chain barriers preventing local farmers from supplying tourist establishments?
Which Caribbean destinations have successfully implemented farm-to-table certification or linkage programs?
What are the quantitative economic impacts and visitor willingness-to-pay for local culinary experiences?""",
    "geography": "Jamaica, Barbados, Saint Lucia, Dominican Republic, Guadeloupe, Martinique",
    "date_range": "2015-2025",
    "report_language": "English",
    "priority_themes": "Agritourism, Local Supply Chain, Import Substitution, Hotel Sourcing, Value Retention",
    "instructions": "Emphasize quantitative metrics, World Bank indicators, verbatim source quotes, and clear policy recommendations."
}


def run_research(brief_data: dict):
    if HAS_RICH and console:
        console.print(Panel(
            f"[bold cyan]Research Topic:[/bold cyan] {brief_data['title']}\n"
            f"[bold cyan]Objective:[/bold cyan] {brief_data['objective']}\n"
            f"[bold cyan]Geography:[/bold cyan] {brief_data.get('geography', 'Caribbean Coverage')}\n"
            f"[bold cyan]Date Range:[/bold cyan] {brief_data.get('date_range', '2015-2025')}",
            title="🌴 [bold green]Eclectik Market Intelligence Agent[/bold green]",
            border_style="green"
        ))
    else:
        print("="*70)
        print(f"🌴 ECLEKTIK MARKET INTELLIGENCE AGENT")
        print(f"Research Topic: {brief_data['title']}")
        print(f"Objective: {brief_data['objective']}")
        print(f"Geography: {brief_data.get('geography', 'Caribbean Coverage')}")
        print(f"Date Range: {brief_data.get('date_range', '2015-2025')}")
        print("="*70)

    print_msg("\n[bold yellow]🚀 Initiating Agentic Research Pipeline...[/bold yellow]\n")

    initial_state = {
        "raw_input": brief_data
    }

    final_state = research_graph.invoke(initial_state)

    print_msg("\n[bold green]═══ Execution Logs ═══[/bold green]")
    for log in final_state.get("logs", []):
        print_msg(f"[dim]•[/dim] {log}")

    report_md = final_state.get("report_markdown", "")
    if report_md:
        print_msg("\n" + "="*80)
        if HAS_RICH and console:
            console.print(Panel("[bold green]Generated Market Intelligence Report[/bold green]", border_style="cyan"))
            console.print(Markdown(report_md))
        else:
            print("\n--- GENERATED MARKET INTELLIGENCE REPORT ---\n")
            print(report_md)

        # Save to output file
        out_dir = CURRENT_DIR.parent / "outputs"
        out_dir.mkdir(exist_ok=True)
        filename = f"research_report_{final_state.get('run_id', 'latest')[:8]}.md"
        out_path = out_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print_msg(f"\n[bold green]✓ Report successfully saved to:[/bold green] [cyan]{out_path}[/cyan]\n")
    else:
        print_msg("[bold red]Failed to generate report.[/bold red]")


if __name__ == "__main__":
    print_msg("[bold blue]Starting Research Intelligence Agent...[/bold blue]")
    run_research(SAMPLE_BRIEF)

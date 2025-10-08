
from rich.console import Console
from rich.panel import Panel

def run_health_check(changes: dict):
    """
    Takes a dictionary of schema changes and prints a formatted health report.
    """
    console = Console()
    console.print("\n[bold]🩺 SQLMorph Schema Health Check 🩺[/bold]\n")
    
    # Check if any of the change lists/dicts are non-empty
    has_issues = any(
        changes.get(key) for key in [
            "new_tables", "orphaned_tables", "new_columns",
            "orphaned_columns", "modified_columns"
        ]
    )

    if not has_issues:
        console.print(Panel("[bold green]✅ Your database schema is perfectly in sync with your models.[/bold green]", title="[bold]Health Status[/bold]", border_style="green"))
        return

    console.print(Panel("[bold yellow]⚠️ Your database schema has drifted from your models. See details below.[/bold yellow]", title="[bold]Health Status[/bold]", border_style="yellow"))

    if changes.get("new_tables"):
        console.print("\n[bold]New Tables (in models, not in DB):[/bold]")
        for table in changes["new_tables"]:
            console.print(f"  [green]+ {table}[/green]")

    if changes.get("orphaned_tables"):
        console.print("\n[bold]Orphaned Tables (in DB, not in models):[/bold]")
        for table in changes["orphaned_tables"]:
            console.print(f"  [red]- {table}[/red]")

    if changes.get("new_columns"):
        console.print("\n[bold]New Columns (in models, not in DB):[/bold]")
        for table, cols in changes["new_columns"].items():
            for col in cols:
                console.print(f"  [green]+ {table}.{col}[/green]")

    if changes.get("orphaned_columns"):
        console.print("\n[bold]Orphaned Columns (in DB, not in models):[/bold]")
        for table, cols in changes["orphaned_columns"].items():
            for col in cols:
                console.print(f"  [red]- {table}.{col}[/red]")
    
    if changes.get("modified_columns"):
        console.print("\n[bold]Modified Columns (type mismatch):[/bold]")
        for change in changes["modified_columns"]:
            console.print(f"  [yellow]! {change}[/yellow]")
    
    console.print("\nRun [bold]`sqlmorph makemigration <name>`[/bold] to generate a migration for these changes.")

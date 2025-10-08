
from rich.console import Console
from rich.panel import Panel

def print_migration_plan(changes: dict):
    """
    Takes a dictionary of schema changes and prints a planned list of operations.
    """
    console = Console()
    console.print("\n[bold]📑 SQLMorph Migration Plan 📑[/bold]\n")

    has_auto_changes = changes.get("new_tables") or changes.get("new_columns")
    has_warnings = changes.get("orphaned_tables") or changes.get("orphaned_columns") or changes.get("modified_columns")

    if not has_auto_changes and not has_warnings:
        console.print(Panel("[bold green]✅ Your database is already in sync. No migration needed.[/bold green]", title="[bold]Plan Status[/bold]", border_style="green"))
        return

    console.print("[bold]A new migration would perform the following operations:[/bold]")

    if changes.get("new_tables"):
        console.print("\n[bold green]Tables to be CREATED:[/bold green]")
        for table in changes["new_tables"]:
            console.print(f"  [green]+ {table}[/green]")

    if changes.get("new_columns"):
        console.print("\n[bold green]Columns to be ADDED:[/bold green]")
        for table, cols in changes["new_columns"].items():
            for col in cols:
                console.print(f"  [green]+ {table}.{col}[/green]")

    if has_warnings:
        console.print("\n[bold yellow]⚠️ Warnings & Potential Future Actions:[/bold yellow]")
        if changes.get("modified_columns"):
            console.print("  [yellow]! Type changes detected. These require manual SQL in the migration file:[/yellow]")
            for change in changes["modified_columns"]:
                console.print(f"    - {change}")
        
        if changes.get("orphaned_tables") or changes.get("orphaned_columns"):
            console.print("  [yellow]! Orphaned objects found. A future migration could be destructive:[/yellow]")
            for table in changes.get("orphaned_tables", []):
                console.print(f"    - Table '{table}' exists in the DB but not in models.")
            for table, cols in changes.get("orphaned_columns", {}).items():
                for col in cols:
                    console.print(f"    - Column '{table}.{col}' exists in the DB but not in models.")

    console.print("\nRun [bold]`sqlmorph makemigration <name>`[/bold] to generate a migration file for these changes.")

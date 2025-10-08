
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

COMMANDS = {
    "Migration & Schema": [
        {
            "name": "makemigration <name>",
            "desc": "Scans models and generates a new migration file."
        },
        {
            "name": "migrate",
            "desc": "Applies pending migrations to the database."
        },
        {
            "name": "rollback",
            "desc": "Reverts the last applied migration."
        },
        {
            "name": "plan",
            "desc": "Shows a preview of the changes a migration would make."
        },
        {
            "name": "doctor",
            "desc": "Checks for schema drift between models and the database."
        },
    ],
    "Inspection & Auditing": [
        {
            "name": "history",
            "desc": "Lists all migrations and their status. Use `--graph` for a visual tree."
        },
        {
            "name": "inspect",
            "desc": "Displays a detailed summary of your models. Use `--format json`."
        },
        {
            "name": "diagram",
            "desc": "Generates a Mermaid.js ERD for model relationships."
        },
        {
            "name": "snapshot",
            "desc": "Saves the current model schema state to a JSON file."
        },
        {
            "name": "explain <query>",
            "desc": "Shows the database's query plan for a given SQL statement."
        },
    ],
    "Development & Utilities": [
        {
            "name": "seed --file <path>",
            "desc": "Populates the database with data from a JSON seed file."
        },
        {
            "name": "watch",
            "desc": "Monitors model files for changes and plans migrations automatically."
        },
        {
            "name": "diffdb --url <db_url>",
            "desc": "Generates SQLModel classes from an existing database."
        },
        {
            "name": "shell",
            "desc": "Opens an interactive shell for the connected database."
        },
        {
            "name": "help",
            "desc": "Shows this help message."
        }
    ]
}

def print_help():
    console = Console()
    
    console.print(Panel(
        "[bold cyan]SQLMorph[/bold cyan] - The missing migration layer for SQLModel.",
        subtitle="[dim]Usage: sqlmorph [COMMAND] [OPTIONS][/dim]",
        border_style="blue"
    ))

    for category, commands in COMMANDS.items():
        table = Table(title=f"[bold]{category}[/bold]", title_style="magenta", show_header=False, box=None)
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description")

        for cmd in commands:
            table.add_row(f"  {cmd['name']}", cmd['desc'])
        
        console.print(table)

    console.print("Run [bold]`sqlmorph [COMMAND] --help`[/bold] for more information on a specific command.")


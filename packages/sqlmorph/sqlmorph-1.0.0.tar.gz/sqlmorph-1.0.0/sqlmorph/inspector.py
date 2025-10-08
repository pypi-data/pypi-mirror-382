
from rich.table import Table
from rich.console import Console
from sqlmodel import SQLModel
import json

from .migrator import _load_models_from_path

def get_schema_details(models_path: str) -> dict:
    """
    Loads models and extracts their schema details, including relationships.
    """
    _load_models_from_path(models_path)
    metadata = SQLModel.metadata
    
    schema = {"tables": {}}
    
    for table_name, table_obj in metadata.tables.items():
        if table_name == 'sqlmorph_migrations':
            continue
            
        schema["tables"][table_name] = {
            "columns": [],
            "relationships": [] # We will now populate this
        }
        for column in table_obj.columns:
            col_info = {
                "name": column.name,
                "type": str(column.type),
                "primary_key": column.primary_key,
                "nullable": column.nullable,
                "default": str(column.default.arg) if column.default else "None",
            }
            schema["tables"][table_name]["columns"].append(col_info)

            # --- NEW: Detect Foreign Keys ---
            if column.foreign_keys:
                for fk in column.foreign_keys:
                    # fk.column gives the target column object (e.g., 'product.id')
                    target_table = fk.column.table.name
                    target_column = fk.column.name
                    
                    relationship_info = {
                        "source_column": column.name,
                        "target_table": target_table,
                        "target_column": target_column,
                    }
                    schema["tables"][table_name]["relationships"].append(relationship_info)

    return schema


def print_schema_as_table(schema: dict):
    """
    Uses the 'rich' library to print the schema details in a formatted table.
    """
    console = Console()
    
    if not schema["tables"]:
        console.print("[bold yellow]No models found to inspect.[/bold yellow]")
        return

    console.print("\n[bold]Inspecting Models Schema[/bold]\n")
    
    for table_name, table_details in schema["tables"].items():
        table = Table(
            title=f"Model: [bold cyan]{table_name.capitalize()}[/bold cyan]",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Column Name", style="white")
        table.add_column("Type", style="green")
        table.add_column("Primary Key", justify="center")
        table.add_column("Nullable", justify="center")
        table.add_column("Default")
        
        for col in table_details["columns"]:
            table.add_row(
                col["name"],
                col["type"],
                "✅" if col["primary_key"] else "",
                "✅" if col["nullable"] else "[red]❌[/red]",
                col["default"]
            )
        console.print(table)
        console.print("") # Adds a spacer line between tables

def print_schema_as_json(schema: dict):
    """

    Prints the schema dictionary as a formatted JSON string.
    """
    console = Console()
    console.print(json.dumps(schema, indent=2))


def print_schema_as_diagram(schema: dict):
    """
    Prints a simple text-based diagram of model relationships.
    """
    console = Console()
    console.print("\n[bold]Inspecting Model Relationships (ERD)[/bold]\n")

    for table_name, table_details in schema["tables"].items():
        console.print(f"[bold cyan]Model: {table_name.capitalize()}[/bold cyan]")
        
        # Print columns (optional, but good for context)
        for col in table_details["columns"]:
            pk_marker = "[dim yellow](PK)[/dim yellow]" if col["primary_key"] else ""
            console.print(f"  - {col['name']} ({col['type']}) {pk_marker}")

        # Print relationships
        if table_details["relationships"]:
            console.print("[bold magenta]  Relationships:[/bold magenta]")
            for rel in table_details["relationships"]:
                console.print(
                    f"    - '{rel['source_column']}' points to "
                    f"[bold green]{rel['target_table']}.{rel['target_column']}[/bold green]"
                )
        console.print("") # Spacer

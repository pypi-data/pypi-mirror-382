
import json
from rich.console import Console
from sqlmodel import SQLModel, Session

from .migrator import _load_models_from_path

def seed_data_from_file(engine, models_path: str, seed_file_path: str):
    """
    Loads data from a JSON file and inserts it into the database.
    """
    console = Console()
    console.print(f"\n[bold]🌱 Seeding data from '{seed_file_path}'...[/bold]\n")

    # 1. Load user models to get access to the classes
    _load_models_from_path(models_path)
    
    # Create a mapping from table names (lowercase) to SQLModel classes
    model_map = {
        model.__tablename__: model
        for model in SQLModel.__subclasses__()
        if hasattr(model, "__tablename__")
    }

    # 2. Read and parse the JSON file
    try:
        with open(seed_file_path, "r") as f:
            data_to_seed = json.load(f)
    except FileNotFoundError:
        console.print(f"[bold red]❌ Error: Seed file not found at '{seed_file_path}'.[/bold red]")
        return
    except json.JSONDecodeError:
        console.print(f"[bold red]❌ Error: Could not parse JSON from '{seed_file_path}'. Please check the file format.[/bold red]")
        return

    # 3. Insert the data
    with Session(engine) as session:
        # The user must order the keys in the JSON file correctly to respect foreign keys
        for table_name, rows in data_to_seed.items():
            model_class = model_map.get(table_name.lower())
            
            if not model_class:
                console.print(f"[yellow]⚠️ Warning: Model for table '{table_name}' not found. Skipping.[/yellow]")
                continue

            console.print(f"  -> Seeding {len(rows)} row(s) into [cyan]{table_name}[/cyan]...")
            for row_data in rows:
                # Create an instance of the model and unpack the row data into it
                instance = model_class(**row_data)
                session.add(instance)
        
        try:
            session.commit()
            console.print("\n[bold green]✅ Seed data successfully committed to the database.[/bold green]")
        except Exception as e:
            console.print(f"\n[bold red]❌ An error occurred during commit: {e}[/bold red]")
            console.print("[bold yellow]Rolling back changes...[/bold yellow]")
            session.rollback()


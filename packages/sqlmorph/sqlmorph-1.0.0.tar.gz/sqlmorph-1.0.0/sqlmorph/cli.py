
import typer
from typing_extensions import Annotated
from sqlmodel import create_engine, SQLModel

from sqlalchemy.schema import CreateTable
import json
from . import migrator
import datetime
import importlib.util
import os
from . import tracker, utils, migrator, inspector, doctorr, planner, seeder, diagram_generator, watcher, model_generator, explainer, db_shell, help_text


app = typer.Typer(
    name="sqlmorph",
    help="SQLModel with Built-in Migrations — no Alembic, no boilerplate.",
    add_completion=False,
)

# Create a global state dictionary to hold the engine
state = {"engine": None}

@app.callback()
def main(
    ctx: typer.Context,
    db: Annotated[str, typer.Option(
        "--db",
        help="The database connection URL.",
        envvar="DATABASE_URL", # Allow setting via environment variable
        rich_help_panel="Connection Settings"
    )] = "sqlite:///database.db",
):
    """
    SQLMorph CLI main entry point.
    Initializes the database engine and tracker table.
    """
    # Create the engine and store it in the state
    engine = create_engine(db)
    state["engine"] = engine

    # Ensure the migration tracker table exists before any command runs
    print("Initializing SQLMorph...")
    tracker.init_tracker_table(engine)
    print("-" * 20)


@app.command()
def makemigration(
    name: str,
    models: Annotated[str, typer.Option(
        "--models",
        help="The path to the file containing your SQLModel definitions.",
        rich_help_panel="File Settings"
    )] = "models.py",
):
    """
    Scans models, diffs the database schema, and creates a new migration file.
    """
    engine = state["engine"]
    print(f"✨ Generating migration for: '{name}'")

    changes = migrator.detect_changes(engine, models_path=models)
    model_metadata = SQLModel.metadata # Get metadata after models are loaded

    # --- Check if there are any auto-generatable changes ---
    has_changes = (
        changes["new_tables"] or
        changes["new_columns"] or
        changes["modified_columns"]
    )
    if not has_changes:
        print("✅ Your models are in sync with the database. No migration needed.")
        # We still check for orphaned objects to warn the user
        if changes["orphaned_tables"] or changes["orphaned_columns"]:
             print("\n[bold yellow]⚠️ Warning: Your database contains orphaned objects not defined in your models.[/bold yellow]")
             print("Run `sqlmorph doctor` for a detailed report.")
        return

    # --- Build Upgrade and Downgrade Commands ---
    upgrade_commands = []
    downgrade_commands = []

    # 1. Handle new tables
    for table_name in changes["new_tables"]:
        table_object = model_metadata.tables[table_name]
        create_sql = str(CreateTable(table_object).compile(engine))
        upgrade_commands.append(create_sql)
        downgrade_commands.append(f"DROP TABLE {table_name}")

    # 2. Handle new columns
    for table_name, col_names in changes["new_columns"].items():
        for col_name in col_names:
            column_object = model_metadata.tables[table_name].c[col_name]
            add_sql = migrator._generate_add_column_sql(table_name, column_object, engine)
            upgrade_commands.append(add_sql)
            downgrade_commands.append(f"ALTER TABLE {table_name} DROP COLUMN {col_name}")

    # --- Generate File Content ---
    migration_filename = utils.generate_migration_filename(name)
    migrations_dir = "migration_files"
    os.makedirs(migrations_dir, exist_ok=True)
    file_path = os.path.join(migrations_dir, migration_filename)

    upgrade_sql = "\n".join([f'        session.exec(text("""{sql}"""))' for sql in upgrade_commands])
    downgrade_sql = "\n".join([f'        session.exec(text("""{sql}"""))' for sql in downgrade_commands])

    # Add comments for detected modifications
    mod_comments = ""
    if changes["modified_columns"]:
        mod_comments += "\n    # The following column modifications were detected:\n"
        for mod in changes["modified_columns"]:
            mod_comments += f"    # - {mod}\n"
        mod_comments += "    # Please add the necessary SQL manually to the upgrade function.\n"

    # Handle SQLite's lack of DROP COLUMN support
    if engine.dialect.name == "sqlite" and any(cmd.startswith("ALTER TABLE") and "DROP COLUMN" in cmd for cmd in downgrade_commands):
        downgrade_sql = (
            "        # SQLite does not support DROP COLUMN.\n"
            "        # Please handle this downgrade manually.\n"
            "        # See: https://www.sqlite.org/lang_altertable.html\n"
            "        pass"
         )

    if not downgrade_sql:
        downgrade_sql = "        print('No downgrade path for this migration.')\n        pass"

    migration_template = f"""
# Migration: {name}
# Generated at: {datetime.datetime.utcnow().isoformat()}

from sqlmodel import Session, text

def upgrade(engine):
    # --- BEGIN AUTOGENERATED CODE ---
    print("Applying schema changes for '{name}'...")
    with Session(engine) as session:
{upgrade_sql}
{mod_comments}
        session.commit()
    # --- END AUTOGENERATED CODE ---

def downgrade(engine):
    # --- BEGIN AUTOGENERATED CODE ---
    print("Reverting schema changes for '{name}'...")
    with Session(engine) as session:
{downgrade_sql}
        session.commit()
    # --- END AUTOGENERATED CODE ---
"""
    with open(file_path, "w") as f:
        f.write(migration_template.strip())

    print(f"✅ Migration file created: {file_path}")




@app.command()
def migrate():
    """
    Runs all unapplied migrations to update the database schema.
    """
    engine = state["engine"]
    migrations_dir = "migration_files"
    print("🚀 Checking for pending migrations...")

    # 1. Get all local migration files and all applied migrations from the DB
    local_migrations = utils.get_migration_files(migrations_dir)
    applied_migrations = tracker.get_applied_migrations(engine)

    # 2. Determine which migrations are pending
    pending_migrations = [
        m for m in local_migrations if m not in applied_migrations
    ]

    if not pending_migrations:
        print("✅ Database is up to date. No migrations to apply.")
        return

    print(f"Found {len(pending_migrations)} pending migration(s). Applying now...")

    for migration_name in pending_migrations:
        print(f"  -> Applying {migration_name}...")
        try:
            # 3. Dynamically import the migration module
            module_name = migration_name.replace('.py', '')
            file_path = os.path.join(migrations_dir, migration_name)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)

            # 4. Execute the upgrade function
            migration_module.upgrade(engine)

            # 5. Record the migration in the database
            tracker.add_migration_record(engine, migration_name)
            print(f"  ✅ Successfully applied and recorded {migration_name}")

        except Exception as e:
            print(f"❌ Error applying migration {migration_name}: {e}")
            print("Migration failed. Halting.")
            # For safety, we stop if one migration fails.
            return

    print("\n🎉 All migrations applied successfully!")



@app.command()
def rollback():
    """
    Reverts the last applied migration.
    """
    engine = state["engine"]
    migrations_dir = "migration_files"
    print("⏪ Attempting to roll back the last migration...")

    # 1. Get the list of applied migrations, sorted chronologically
    applied_migrations = tracker.get_applied_migrations(engine)
    if not applied_migrations:
        print("No migrations have been applied yet. Nothing to roll back.")
        return

    # The last applied migration is the last one in the sorted list
    last_migration_name = applied_migrations[-1]
    print(f"Last applied migration is: {last_migration_name}")

    try:
        # 2. Dynamically import the migration module
        module_name = last_migration_name.replace('.py', '')
        file_path = os.path.join(migrations_dir, last_migration_name)
        
        if not os.path.exists(file_path):
            print(f"❌ Error: Migration file not found: {file_path}")
            print("Cannot perform rollback without the migration file.")
            return

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        migration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_module)

        # 3. Execute the downgrade function
        migration_module.downgrade(engine)

        # 4. Remove the migration record from the database
        tracker.remove_migration_record(engine, last_migration_name)
        print(f"✅ Successfully rolled back and removed record for {last_migration_name}")

    except Exception as e:
        print(f"❌ Error during rollback of {last_migration_name}: {e}")
        print("Rollback failed. The database might be in an inconsistent state.")
        return


@app.command()
def history(
    graph: Annotated[bool, typer.Option(
        "--graph",
        help="Display the migration history as a visual graph.",
        rich_help_panel="Display Settings"
    )] = False,
):
    """
    Lists all migrations and their status (applied or pending).
    """
    engine = state["engine"]
    migrations_dir = "migration_files"
    print("📜 Migration History:")

    local_files = utils.get_migration_files(migrations_dir)
    applied_records = set(tracker.get_applied_migrations(engine))

    if graph:
        tracker.print_history_as_graph(local_files, applied_records)
        return

    # --- Fallback to the original list view if --graph is not used ---
    if not local_files:
        print("No migration files found.")
        # ... (existing logic for handling missing files) ...
        return

    all_migrations_with_status = []
    for filename in local_files:
        status = "[APPLIED]" if filename in applied_records else "[PENDING]"
        all_migrations_with_status.append((filename, status))

    max_len = max(len(f) for f, s in all_migrations_with_status) if all_migrations_with_status else 0
    for filename, status in all_migrations_with_status:
        padding = " " * (max_len - len(filename))
        color = "green" if status == "[APPLIED]" else "yellow"
        print(f"- {filename}{padding}  [{color}]{status}[/{color}]")
    # Bonus: Check for applied migrations whose files are missing
    missing_files = applied_records - set(local_files)
    if missing_files:
        print("\n⚠️ Warning: These migrations are recorded in the database but their files are missing:")
        for record in sorted(list(missing_files)):
            print(f"- {record}")


@app.command()
def inspect(
    models: Annotated[str, typer.Option(
        "--models",
        help="The path to the file containing your SQLModel definitions.",
        rich_help_panel="File Settings"
    )] = "models.py",
    format: Annotated[str, typer.Option(
        "--format",
        help="The output format for the schema inspection.",
        rich_help_panel="Display Settings"
    )] = "table",
):
    """
    Displays a summary of your SQLModels.
    """
    print("🔍 Inspecting models...")
    try:
        schema_details = inspector.get_schema_details(models_path=models)
        
        if format.lower() == "json":
            inspector.print_schema_as_json(schema_details)
        elif format.lower() == "diagram": # <-- ADD THIS BLOCK
            inspector.print_schema_as_diagram(schema_details)
        elif format.lower() == "table":
            inspector.print_schema_as_table(schema_details)
        else:
            print(f"❌ Error: Invalid format '{format}'. Please use 'table', 'json', or 'diagram'.")

    except FileNotFoundError:
        print(f"❌ Error: The models file was not found at '{models}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

@app.command()
def doctor(
    models: Annotated[str, typer.Option(
        "--models",
        help="The path to the file containing your SQLModel definitions.",
        rich_help_panel="File Settings"
    )] = "models.py",
):
    """
    Checks for inconsistencies between your models and the database.
    """
    engine = state["engine"]
    print("🩺 Running schema health check...")
    
    changes = migrator.detect_changes(engine, models_path=models)
    doctorr.run_health_check(changes)


@app.command()
def plan(
    models: Annotated[str, typer.Option(
        "--models",
        help="The path to the file containing your SQLModel definitions.",
        rich_help_panel="File Settings"
    )] = "models.py",
):
    """
    Shows a preview of the changes that `makemigration` will generate.
    """
    engine = state["engine"]
    print("📑 Planning migration...")
    
    changes = migrator.detect_changes(engine, models_path=models)
    planner.print_migration_plan(changes)


@app.command()
def seed(
    file: Annotated[str, typer.Option(
        "--file",
        help="Path to the JSON or YAML seed file.",
        rich_help_panel="Data Seeding"
    )],
    models: Annotated[str, typer.Option(
        "--models",
        help="The path to the file containing your SQLModel definitions.",
        rich_help_panel="File Settings"
    )] = "models.py",
):
    """
    Populates the database with seed data from a file.
    """
    engine = state["engine"]
    seeder.seed_data_from_file(engine, models_path=models, seed_file_path=file)



@app.command()
def diagram(
    models: Annotated[str, typer.Option(
        "--models",
        help="The path to the file containing your SQLModel definitions.",
        rich_help_panel="File Settings"
    )] = "models.py",
    format: Annotated[str, typer.Option(
        "--format",
        help="The output format for the diagram (e.g., 'mermaid').",
        rich_help_panel="Display Settings"
    )] = "mermaid",
):
    """
    Generates a relationship diagram from your models.
    """
    # We can reuse the inspector's logic to get the schema details
    schema_details = inspector.get_schema_details(models_path=models)
    diagram_generator.print_diagram(schema_details, format=format)



@app.command()
def watch(
    models: Annotated[str, typer.Option(
        "--models",
        help="The path to the file containing your SQLModel definitions.",
        rich_help_panel="File Settings"
    )] = "models.py",
):
    """
    Watches model files for changes and prompts for migrations.
    """
    engine = state["engine"]
    watcher.start_watching(engine, models_path=models)

@app.command()
def diffdb(
    url: Annotated[str, typer.Option(
        "--url",
        help="The connection URL of the database to inspect.",
        rich_help_panel="Database Connection"
    )],
    out: Annotated[str, typer.Option(
        "--out",
        help="The name of the Python file to write the models to.",
        rich_help_panel="Output Settings"
    )] = "models_generated.py",
):
    """
    Generates SQLModel classes from an existing database schema.
    """
    try:
        generated_code = model_generator.generate_models_from_db(db_url=url)
        with open(out, "w") as f:
            f.write(generated_code)
        print(f"✅ Models successfully written to '{out}'.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")


@app.command()
def snapshot(
    models: Annotated[str, typer.Option(
        "--models",
        help="The path to the file containing your SQLModel definitions.",
        rich_help_panel="File Settings"
    )] = "models.py",
    name: Annotated[str, typer.Option(
        "--name",
        help="An optional descriptive name for the snapshot file."
    )] = "schema_snapshot",
):
    """
    Saves the current model schema state to a timestamped JSON file.
    """
    print("📸 Creating schema snapshot...")
    try:
        schema_details = inspector.get_schema_details(models_path=models)
        
        # Generate a timestamped filename
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{name}.json"
        
        # Write the JSON data to the file
        with open(filename, "w") as f:
            json.dump(schema_details, f, indent=2)
            
        print(f"✅ Snapshot successfully saved to '{filename}'.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")




@app.command()
def explain(
    query: Annotated[str, typer.Argument(
        help="The raw SQL query to explain."
    )],
):
    """
    Shows the database's query plan for a given SQL statement.
    """
    engine = state["engine"]
    explainer.explain_query(engine, query=query)



@app.command()
def shell():
    """
    Opens an interactive shell for the connected database.
    """
    engine = state["engine"]
    db_shell.launch_shell(engine)


@app.command(name="help")
def show_help():
    """
    Shows a detailed overview of all available commands.
    """
    help_text.print_help()


if __name__ == "__main__":
    app()

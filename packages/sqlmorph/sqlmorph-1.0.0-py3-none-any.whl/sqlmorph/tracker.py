
from datetime import datetime
from typing import List, Optional
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from sqlmodel import Field, Session, SQLModel, create_engine, select

# 1. Define the model for our internal migration tracking table.
class SQLMorphMigration(SQLModel, table=True):
    """
    Represents a single applied migration in the database.
    This model corresponds to the `sqlmorph_migrations` table.
    """
    __tablename__ = "sqlmorph_migrations"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # e.g., "20251007_create_user_table"
    applied_at: datetime = Field(default_factory=datetime.utcnow)


def init_tracker_table(engine):
    """
    Ensures the `sqlmorph_migrations` table exists in the database.
    """
    with Session(engine) as session:
        # The SQLModel.metadata.create_all() method is idempotent.
        # It will only create tables that do not already exist.
        SQLMorphMigration.metadata.create_all(engine)
        session.commit()
    print("✅ Migration tracker table initialized.")


def get_applied_migrations(engine) -> List[str]:
    """
    Retrieves a list of all migration names that have been applied.

    Args:
        engine: The SQLAlchemy engine connected to the target database.

    Returns:
        A list of migration names (e.g., ['20251007_create_user_table']).
    """
    with Session(engine) as session:
        statement = select(SQLMorphMigration.name)
        results = session.exec(statement).all()
        return results

def add_migration_record(engine, migration_name: str):
    """
    Adds a new record to the `sqlmorph_migrations` table.

    Args:
        engine: The SQLAlchemy engine.
        migration_name: The name of the migration to record.
    """
    with Session(engine) as session:
        migration = SQLMorphMigration(name=migration_name)
        session.add(migration)
        session.commit()
    print(f"✅ Recorded migration: {migration_name}")

def remove_migration_record(engine, migration_name: str):
    """
    Removes a record from the `sqlmorph_migrations` table (for rollbacks).

    Args:
        engine: The SQLAlchemy engine.
        migration_name: The name of the migration to remove.
    """
    with Session(engine) as session:
        statement = select(SQLMorphMigration).where(SQLMorphMigration.name == migration_name)
        migration_to_delete = session.exec(statement).first()
        if migration_to_delete:
            session.delete(migration_to_delete)
            session.commit()
            print(f"✅ Rolled back migration record: {migration_name}")
        else:
            print(f"⚠️ Could not find migration record to roll back: {migration_name}")

def print_history_as_graph(all_migrations: list, applied_migrations: set):
    """
    Uses 'rich' to print the migration history as a visual graph.
    """
    console = Console()
    
    if not all_migrations:
        console.print(Panel("[bold yellow]No migration files found.[/bold yellow]", title="Migration History", border_style="yellow"))
        return

    tree = Tree(
        "[bold]Migration History[/bold]",
        guide_style="bold bright_blue",
    )

    for i, migration_name in enumerate(all_migrations):
        is_applied = migration_name in applied_migrations
        
        if is_applied:
            status_marker = "[bold green][APPLIED][/bold green]"
            node_style = "green"
        else:
            status_marker = "[bold yellow][PENDING][/bold yellow]"
            node_style = "yellow"
            
        # For the last node, don't add a connecting line down
        is_last = i == len(all_migrations) - 1
        
        node_text = f"[{node_style}]{migration_name}[/{node_style}] {status_marker}"
        
        if is_last:
            tree.add(node_text)
        else:
            # Add a child to the previous node to create the chain
            if i == 0:
                branch = tree.add(node_text)
            else:
                branch = branch.add(node_text)

    console.print(tree)

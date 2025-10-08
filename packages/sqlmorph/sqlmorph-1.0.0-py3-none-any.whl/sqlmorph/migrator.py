from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.schema import CreateTable, AddConstraint
from sqlmodel import SQLModel
import importlib.util
import sys
from typing import List, Tuple, Dict, Any


def _load_models_from_path(path: str):
    """
    Dynamically imports all modules in a given path to ensure their
    SQLModel definitions are registered with the global SQLModel.metadata.
    """
    # This is a simplified way to load user models.
    # We assume models are in a file like 'models.py'.
    # A more robust solution might search a directory.
    spec = importlib.util.spec_from_file_location("models", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["models"] = module
    spec.loader.exec_module(module)
    print(f"🔍 Discovered models from: {path}")



def _generate_add_column_sql(table_name: str, column: 'Column', engine) -> str:
    """Generates the 'ALTER TABLE ADD COLUMN' SQL statement."""
    column_name = column.name
    column_type = column.type.compile(engine.dialect)
    nullable = "NULL" if column.nullable else "NOT NULL"
    
    default_clause = ""
    if column.default is not None:
        # Handle boolean defaults correctly for different DBs
        if isinstance(column.default.arg, bool) and engine.dialect.name in ['postgresql', 'mysql']:
             default_val = 'true' if column.default.arg else 'false'
        elif isinstance(column.default.arg, bool) and engine.dialect.name == 'sqlite':
             default_val = '1' if column.default.arg else '0'
        elif isinstance(column.default.arg, str):
            default_val = f"'{column.default.arg}'"
        else:
            default_val = str(column.default.arg)
        default_clause = f"DEFAULT {default_val}"

    return f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {nullable} {default_clause}".strip()



def detect_new_tables(engine, models_path: str) -> List[str]:
    """
    Compares the models in the code with the database schema to find new tables
    and generates the SQL for their creation.

    Args:
        engine: The SQLAlchemy engine for database connection.
        models_path: The file path to the user's models (e.g., 'models.py').

    Returns:
        A list of SQL 'CREATE TABLE' statements for newly detected tables.
    """
    # 1. Load user models to populate SQLModel.metadata
    _load_models_from_path(models_path)
    model_metadata = SQLModel.metadata

    # 2. Reflect the current database schema
    db_metadata = MetaData()
    db_metadata.reflect(bind=engine)

    # 3. Compare and find new tables
    model_tables = set(model_metadata.tables.keys())
    db_tables = set(db_metadata.tables.keys())
    
    # Find tables that are in our models but not in the database
    # We also exclude our internal migration table
    new_table_names = model_tables - db_tables - {'sqlmorph_migrations'}

    if not new_table_names:
        print("✅ Database schema is up to date. No new tables found.")
        return []

    print(f"✨ Found {len(new_table_names)} new table(s): {', '.join(new_table_names)}")

    # 4. Generate 'CREATE TABLE' SQL for each new table
    sql_commands = []
    for table_name in new_table_names:
        table_object = model_metadata.tables[table_name]
        # Generate the CREATE TABLE statement for the specific table
        create_sql = str(CreateTable(table_object).compile(engine))
        sql_commands.append(create_sql)

    return sql_commands




def detect_changes(engine, models_path: str) -> Dict[str, Any]:
    """
    Compares models with the database to detect all differences.

    Returns:
        A dictionary summarizing all detected changes:
        {
            "new_tables": [...],
            "orphaned_tables": [...],
            "new_columns": {table: [cols]},
            "orphaned_columns": {table: [cols]},
            "modified_columns": [...],
        }
    """
    _load_models_from_path(models_path)
    model_metadata = SQLModel.metadata
    inspector = inspect(engine)

    # --- Compare Tables ---
    model_table_names = set(model_metadata.tables.keys())
    db_table_names = set(inspector.get_table_names())
    
    new_tables = list(model_table_names - db_table_names - {'sqlmorph_migrations'})
    orphaned_tables = list(db_table_names - model_table_names - {'sqlmorph_migrations'})

    # --- Compare Columns and Types ---
    new_columns: Dict[str, List[str]] = {}
    orphaned_columns: Dict[str, List[str]] = {}
    modified_columns: List[str] = []
    
    common_tables = model_table_names.intersection(db_table_names)
    for table_name in common_tables:
        model_cols = {c.name: c for c in model_metadata.tables[table_name].columns}
        db_cols = {c['name']: c for c in inspector.get_columns(table_name)}
        
        # Find new columns (in model, not in DB)
        added_col_names = set(model_cols.keys()) - set(db_cols.keys())
        if added_col_names:
            new_columns[table_name] = list(added_col_names)

        # Find orphaned columns (in DB, not in model)
        removed_col_names = set(db_cols.keys()) - set(model_cols.keys())
        if removed_col_names:
            orphaned_columns[table_name] = list(removed_col_names)

        # Find modified columns (type changes in common columns)
        for col_name in set(model_cols.keys()).intersection(set(db_cols.keys())):
            model_type_sql = model_cols[col_name].type.compile(engine.dialect)
            db_type_sql = db_cols[col_name]['type'].compile(engine.dialect)

            if model_type_sql.upper() != db_type_sql.upper():
                change_desc = (
                    f"Column '{table_name}.{col_name}' has a type change: "
                    f"from {db_type_sql} to {model_type_sql}"
                )
                modified_columns.append(change_desc)

    return {
        "new_tables": new_tables,
        "orphaned_tables": orphaned_tables,
        "new_columns": new_columns,
        "orphaned_columns": orphaned_columns,
        "modified_columns": modified_columns,
    }

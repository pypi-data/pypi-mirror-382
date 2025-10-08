
from sqlalchemy import create_engine, inspect, MetaData
from rich.console import Console

# A mapping from common SQLAlchemy types to Python type hints
TYPE_MAP = {
    "INTEGER": "int",
    "SMALLINT": "int",
    "BIGINT": "int",
    "VARCHAR": "str",
    "TEXT": "str",
    "CHAR": "str",
    "FLOAT": "float",
    "NUMERIC": "float",
    "DECIMAL": "float",
    "BOOLEAN": "bool",
    "DATE": "datetime.date",
    "DATETIME": "datetime.datetime",
    "TIMESTAMP": "datetime.datetime",
}

def generate_models_from_db(db_url: str) -> str:
    """
    Connects to a database, reflects its schema, and generates SQLModel class definitions.
    """
    console = Console()
    console.print(f"🔗 Connecting to database and reflecting schema...")
    
    engine = create_engine(db_url)
    inspector = inspect(engine)
    metadata = MetaData()
    
    metadata.reflect(bind=engine)
    
    output_code = "from typing import Optional\n"
    output_code += "from datetime import date, datetime\n"
    output_code += "from sqlmodel import SQLModel, Field\n\n"

    for table_name, table_obj in metadata.tables.items():
        # We don't want to generate a model for our internal migration table
        if table_name == 'sqlmorph_migrations':
            continue

        class_name = table_name.capitalize()
        output_code += f"\nclass {class_name}(SQLModel, table=True):\n"
        
        try:
            pk_constraint = inspector.get_pk_constraint(table_name)
            pk_cols = set(pk_constraint['constrained_columns'])
        except (KeyError, TypeError):
            # Handles cases where a table might not have a primary key
            pk_cols = set()

        for column in table_obj.columns:
            col_name = column.name
            col_type_str = str(column.type).split('(')[0]
            py_type = TYPE_MAP.get(col_type_str.upper(), "str") # Use .upper() for safety

            field_args = []
            
            is_pk = col_name in pk_cols
            if is_pk and len(pk_cols) == 1:
                py_type = f"Optional[{py_type}]"
                field_args.append("default=None")
                field_args.append("primary_key=True")
            elif column.nullable:
                py_type = f"Optional[{py_type}]"
                field_args.append("default=None")

            if column.foreign_keys:
                fk = list(column.foreign_keys)[0]
                field_args.append(f'foreign_key="{fk.target_fullname}"')

            field_str = f'Field({", ".join(field_args)})' if field_args else ""
            
            output_code += f"    {col_name}: {py_type}"
            if field_str:
                output_code += f" = {field_str}"
            output_code += "\n"

    console.print("✅ Schema reflection complete. Models generated.")
    return output_code


from rich.console import Console

def generate_mermaid_diagram(schema: dict) -> str:
    """
    Generates an Entity-Relationship Diagram in Mermaid.js syntax.
    """
    mermaid_string = "erDiagram\n"

    # First, define all the tables and their columns
    for table_name, table_details in schema["tables"].items():
        mermaid_string += f"    {table_name.capitalize()} {{\n"
        for col in table_details["columns"]:
            col_type = col["type"].split('(')[0] # Simplify type for diagram (e.g., VARCHAR(100) -> VARCHAR)
            pk_marker = " PK" if col["primary_key"] else ""
            fk_marker = " FK" if any(rel['source_column'] == col['name'] for rel in table_details.get('relationships', [])) else ""
            mermaid_string += f"        {col_type} {col['name']}{pk_marker}{fk_marker}\n"
        mermaid_string += "    }\n\n"

    # Second, define all the relationships between the tables
    for table_name, table_details in schema["tables"].items():
        if table_details["relationships"]:
            for rel in table_details["relationships"]:
                source_table = table_name.capitalize()
                target_table = rel["target_table"].capitalize()
                # Mermaid syntax for one-to-many relationship
                mermaid_string += f'    {target_table} ||--o{{ {source_table} : "has"\n'
    
    return mermaid_string

def print_diagram(schema: dict, format: str):
    """
    Prints the schema in the specified diagram format.
    """
    console = Console()
    if format.lower() == 'mermaid':
        diagram_str = generate_mermaid_diagram(schema)
        # just print the raw string, so the user can pipe it to a file
        print(diagram_str)
    else:
        console.print(f"[bold red]Error: Unsupported diagram format '{format}'.[/bold red]")


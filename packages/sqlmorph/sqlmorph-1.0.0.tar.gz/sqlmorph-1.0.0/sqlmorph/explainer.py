from rich.console import Console
from rich.table import Table
from sqlalchemy import text

def explain_query(engine, query: str):
    """
    Executes EXPLAIN QUERY PLAN on a given SQL query and prints the result.
    """
    console = Console()
    console.print(f"\n[bold]🔎 Explaining Query Plan...[/bold]\n")

    # Basic protection against multiple statements; not a full security measure.
    if ";" in query and not query.strip().endswith(";"):
        console.print("[bold red]❌ Error: Only a single SQL statement is allowed.[/bold red]")
        return

    # The EXPLAIN syntax can vary. EXPLAIN QUERY PLAN is good for SQLite.
    # For PostgreSQL/MySQL, it would just be "EXPLAIN".
    explain_command = f"EXPLAIN QUERY PLAN {query}"
    if engine.dialect.name in ['postgresql', 'mysql']:
        explain_command = f"EXPLAIN {query}"

    try:
        with engine.connect() as connection:
            result = connection.execute(text(explain_command))
            rows = result.fetchall()
            
            if not rows:
                console.print("[yellow]⚠️ The database did not return a query plan.[/yellow]")
                return

            # Create a Rich table to display the results
            table = Table(title="Query Execution Plan", show_header=True, header_style="bold magenta")
            
            # The column names depend on the database's EXPLAIN output
            column_names = result.keys()
            for col_name in column_names:
                table.add_column(col_name.capitalize(), style="dim")

            for row in rows:
                # Convert all row items to strings for Rich
                table.add_row(*[str(item) for item in row])
            
            console.print(table)

    except Exception as e:
        console.print(f"[bold red]❌ An error occurred while executing the query: {e}[/bold red]")


import subprocess
import os
from rich.console import Console
import tempfile


def launch_shell(engine):
    """
    Launches a database-specific interactive shell.
    """
    console = Console()
    dialect = engine.dialect.name

    console.print(f"🗄️ Launching interactive shell for [bold cyan]{dialect}[/bold cyan]...")

    if dialect == 'sqlite':
        _launch_sqlite_shell(engine, console)
    elif dialect == 'postgresql':
        _launch_psql_shell(engine, console)
    elif dialect == 'mysql':
        _launch_mysql_shell(engine, console)
    else:
        console.print(f"[bold red]❌ Error: Interactive shell for '{dialect}' is not supported.[/bold red]")

def _launch_sqlite_shell(engine, console):
    db_path = engine.url.database
    if not db_path:
        console.print("[bold red]❌ Error: Database path not found for SQLite connection.[/bold red]")
        return
    
    console.print(f"Connecting to: {db_path}")
    console.print("Tip: Type '.quit' to exit the shell.")
    
    # Define commands as a list to ensure they are on separate lines
    init_command_list = [
        ".headers on",
        ".mode box",
        "SELECT 'Welcome to the SQLMorph shell for SQLite!' AS ' ';"
    ]
    # Join them with newlines to create the final script
    init_script = "\n".join(init_command_list)
    
    # Create a temporary file to hold the init commands
    with tempfile.NamedTemporaryFile(mode='w', delete=True, suffix='.sql') as temp_init_file:
        temp_init_file.write(init_script)
        temp_init_file.flush()

        try:
            subprocess.run(['sqlite3', db_path, '-init', temp_init_file.name], check=True)
        except FileNotFoundError:
            console.print("[bold red]❌ Error: 'sqlite3' command-line tool not found.[/bold red]")
            console.print("Please make sure it is installed and in your system's PATH.")
        except Exception as e:
            c

    # The temporary file is automatically deleted when the 'with' block exits

def _launch_psql_shell(engine, console):
    # This requires the 'psql' command-line tool to be installed and in the PATH
    conn_args = engine.url.translate_connect_args()
    env = os.environ.copy()
    if conn_args.get('password'):
        env['PGPASSWORD'] = conn_args['password']

    cmd = ['psql']
    if conn_args.get('host'): cmd.extend(['-h', conn_args['host']])
    if conn_args.get('port'): cmd.extend(['-p', str(conn_args['port'])])
    if conn_args.get('username'): cmd.extend(['-U', conn_args['username']])
    if conn_args.get('database'): cmd.append(conn_args['database'])
    
    try:
        subprocess.run(cmd, env=env, check=True)
    except FileNotFoundError:
        console.print("[bold red]❌ Error: 'psql' command-line tool not found.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")

def _launch_mysql_shell(engine, console):
    # This requires the 'mysql' command-line tool to be installed and in the PATH
    conn_args = engine.url.translate_connect_args()
    env = os.environ.copy()
    if conn_args.get('password'):
        env['MYSQL_PWD'] = conn_args['password']

    cmd = ['mysql']
    if conn_args.get('host'): cmd.extend(['-h', conn_args['host']])
    if conn_args.get('port'): cmd.extend(['-P', str(conn_args['port'])]) # Note: -P is uppercase for MySQL
    if conn_args.get('username'): cmd.extend(['-u', conn_args['username']])
    if conn_args.get('database'): cmd.append(conn_args['database'])

    try:
        subprocess.run(cmd, env=env, check=True)
    except FileNotFoundError:
        console.print("[bold red]❌ Error: 'mysql' command-line tool not found.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")

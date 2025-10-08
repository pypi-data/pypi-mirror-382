
import time
from rich.console import Console
from watchdog.observers.polling import PollingObserver as Observer 

from watchdog.events import FileSystemEventHandler

from . import migrator, planner, utils
import os

class ModelChangeHandler(FileSystemEventHandler):
    def __init__(self, engine, models_path):
        self.engine = engine
        self.models_path = models_path
        self.console = Console()
        self.console.print(f"[bold green]👀 Watching for changes in '{self.models_path}'...[/bold green]")

    def on_modified(self, event):
        # This event triggers on any modification, so we check if it's our target file
        if event.src_path.endswith(self.models_path):
            self.console.print(f"\n[bold yellow]File '{self.models_path}' changed. Checking for schema differences...[/bold yellow]")
            
            try:
                changes = migrator.detect_changes(self.engine, self.models_path)
                has_changes = (
                    changes.get("new_tables") or
                    changes.get("new_columns") or
                    changes.get("modified_columns")
                )

                if not has_changes:
                    self.console.print("[green]✅ No schema changes detected.[/green]")
                    return

                # If changes are found, show the plan
                self.console.print("\n[bold]Schema changes detected![/bold]")
                planner.print_migration_plan(changes)
                
                # Here you could add a prompt to auto-run makemigration
                # For now, we'll just notify the user.

            except Exception as e:
                self.console.print(f"[bold red]❌ An error occurred while checking for changes: {e}[/bold red]")


def start_watching(engine, models_path: str):
    event_handler = ModelChangeHandler(engine, models_path)
    observer = Observer()
    # We watch the directory containing the file, not the file itself, as this is more reliable
    path_to_watch = os.path.dirname(os.path.abspath(models_path))
    observer.schedule(event_handler, path_to_watch, recursive=False)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("\n[bold blue]👋 Watcher stopped.[/bold blue]")


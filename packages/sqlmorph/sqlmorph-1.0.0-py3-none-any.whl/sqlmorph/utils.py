import os
import datetime
import re
from typing import List

def generate_migration_filename(description: str) -> str:
    """
    Generates a standardized, timestamped filename for a new migration.

    Args:
        description: A short, descriptive name for the migration
                     (e.g., "add_user_email").

    Returns:
        A formatted filename string (e.g., "20251007130000_add_user_email.py").
    """
    # Get the current UTC time
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")

    # Sanitize the description to make it a valid filename component
    # 1. Replace spaces and hyphens with underscores
    # 2. Remove any characters that are not alphanumeric or underscores
    # 3. Convert to lowercase
    sanitized_description = re.sub(r'[\s-]+', '_', description)
    sanitized_description = re.sub(r'[^a-zA-Z0-9_]', '', sanitized_description).lower()

    # Combine them into the final filename
    filename = f"{timestamp}_{sanitized_description}.py"

    return filename


def get_migration_files(migrations_dir: str = "migration_files") -> List[str]:
    """
    Scans the migration directory and returns a sorted list of migration filenames.

    Args:
        migrations_dir: The directory where migration files are stored.

    Returns:
        A sorted list of filenames (e.g., ['20251007_...py', '20251008_...py']).
    """
    if not os.path.isdir(migrations_dir):
        return []

    files = [
        f for f in os.listdir(migrations_dir)
        if f.endswith(".py") and not f.startswith("__")
    ]
    files.sort()  # Sorts files chronologically based on the timestamp prefix
    return files

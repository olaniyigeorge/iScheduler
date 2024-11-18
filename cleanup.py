import os
import shutil

# Set the root directory of your project
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Specify the folder(s) to ignore (e.g., venv)
IGNORE_FOLDERS = ['venv']

def should_ignore(folder_path):
    """Check if a folder path should be ignored based on IGNORE_FOLDERS."""
    for ignore_folder in IGNORE_FOLDERS:
        if ignore_folder in folder_path.split(os.sep):
            return True
    return False

def delete_pycache_folders():
    """Delete all __pycache__ folders in the project, ignoring certain directories."""
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if should_ignore(root):
            continue

        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            print(f"Deleting: {pycache_path}")
            shutil.rmtree(pycache_path)

def clean_migrations_folders():
    """Delete all files in migration folders except __init__.py, ignoring certain directories."""
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if should_ignore(root):
            continue

        if "migrations" in dirs:
            migrations_path = os.path.join(root, "migrations")
            for file_name in os.listdir(migrations_path):
                file_path = os.path.join(migrations_path, file_name)
                if file_name != "__init__.py" and os.path.isfile(file_path):
                    print(f"Deleting: {file_path}")
                    os.remove(file_path)

# if __name__ == "__main__":
delete_pycache_folders()
clean_migrations_folders()
print("Cleanup complete!")
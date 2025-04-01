import os


PROJECT_REPOSITORY_PATH: str | None = None

def set_project_repository_path(path: str) -> None:
    """
    Set the global project repository path.
    """
    if not os.path.isdir(path):
        print(f"Invalid path: {path}. Please provide a valid directory.")
        return None
    global PROJECT_REPOSITORY_PATH
    PROJECT_REPOSITORY_PATH = path
from pathlib import Path


def assert_exists(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist or is not a file: {path}")

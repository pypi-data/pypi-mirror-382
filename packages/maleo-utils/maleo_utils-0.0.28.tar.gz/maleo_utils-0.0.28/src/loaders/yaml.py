import yaml
from pathlib import Path
from typing import Any
from maleo.types.misc import PathOrString


def from_path(path: PathOrString) -> Any:
    file_path = Path(path)

    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    with file_path.open("r") as f:
        return yaml.safe_load(f)


def from_string(string: str) -> Any:
    return yaml.safe_load(string)

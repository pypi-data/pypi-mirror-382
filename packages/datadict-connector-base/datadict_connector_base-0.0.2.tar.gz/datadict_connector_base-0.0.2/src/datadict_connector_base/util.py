from io import StringIO
from pathlib import Path
from typing import Dict

from ruamel.yaml import YAML


def parse_yaml_string(content: str) -> dict:
    """
    Parse a YAML string into a dict.

    Args:
        content: YAML content as string

    Returns:
        Parsed YAML content as dict
    """
    yaml = YAML(typ="safe")
    return yaml.load(content)


def dump_yaml_string(data: dict) -> str:
    """
    Dump a dict to a YAML string.

    Args:
        data: Data to serialize as YAML

    Returns:
        YAML string
    """
    yaml = YAML()
    yaml.default_flow_style = False
    stream = StringIO()
    yaml.dump(data, stream)
    return stream.getvalue()


def read_yaml_file(file_path: Path) -> dict:
    """
    Read a YAML file from filesystem.

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML content as dict
    """
    yaml = YAML(typ="safe")
    with open(file_path, "r") as f:
        return yaml.load(f)


def write_yaml_file(file_path: Path, data: dict) -> None:
    """
    Write data to a YAML file.

    Args:
        file_path: Path to write to
        data: Data to write as YAML
    """
    yaml = YAML()
    yaml.default_flow_style = False
    with open(file_path, "w") as f:
        yaml.dump(data, f)


def load_yaml_files_from_directory(directory: Path, pattern: str = "**/*.yml") -> Dict[str, str]:
    """
    Load all YAML files from a directory into a normalized dict.

    This is a helper function for the CLI to prepare file contents for loaders.
    Handles path normalization (forward slashes, relative to directory).

    Args:
        directory: Root directory to scan
        pattern: Glob pattern for files to load (default: **/*.yml)

    Returns:
        Dict mapping normalized relative paths to file contents
        Example: {"models/customers.yml": "name: customers\n...",
                 "database.yml": "databases:\n  - name: mydb\n..."}
    """
    files = {}
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            relative_path = file_path.relative_to(directory)
            # Normalize to forward slashes for cross-platform compatibility
            normalized_path = str(relative_path).replace("\\", "/")
            files[normalized_path] = file_path.read_text(encoding="utf-8")
    return files

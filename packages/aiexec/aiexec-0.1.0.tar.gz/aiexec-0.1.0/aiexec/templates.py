from __future__ import annotations

from pathlib import Path
from typing import Iterable, List


TEMPLATE = """\
model: {model}
goal: "Describe the goal for your automation."
permissions:
  - shell
  - file_write
workdir: .
"""


def create_template(path: Path, *, model: str = "local") -> bool:
    """
    Create a template .ai file. Returns False if the file already exists.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return False

    content = TEMPLATE.format(model=model)
    path.write_text(content, encoding="utf-8")
    return True


def discover_scripts(directory: Path) -> List[Path]:
    """
    Return a sorted list of .ai scripts in the directory (non-recursive).
    """
    if not directory.exists():
        return []

    scripts: Iterable[Path] = directory.glob("*.ai")
    results: List[Path] = []
    for script in scripts:
        try:
            results.append(script.resolve().relative_to(directory.resolve()))
        except ValueError:
            results.append(script.resolve())
    return sorted(results)

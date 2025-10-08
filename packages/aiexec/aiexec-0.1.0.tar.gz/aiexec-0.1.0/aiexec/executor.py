from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DANGEROUS = re.compile(
    r"\b("  # broad catch for obviously dangerous patterns
    r"rm\s+-rf"
    r"|sudo\s+"
    r"|chmod\s+777"
    r"|mkfs"
    r"|dd\s+if="
    r"|:(){:|:&};:"
    r"|chown\s+-R\s+/"
    r"|curl\s+[^\n]*\|\s*(?:sh|bash)"
    r"|wget\s+[^\n]*\|\s*(?:sh|bash)"
    r")"
)


@dataclass
class CommandResult:
    command: str
    output: str
    returncode: int
    skipped: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.skipped


def needs_confirm(command: str) -> bool:
    return bool(DANGEROUS.search(command))


def allowed(permission_list: Iterable[str], needed: str) -> bool:
    return needed in permission_list


def safe_run(command: str, cwd: Path, *, timeout: int = 30) -> CommandResult:
    cmd = command.strip()
    if "\n" in cmd:
        return CommandResult(command=cmd, output="Error: multiline commands are not allowed.", returncode=1)

    try:
        completed = subprocess.run(
            cmd,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return CommandResult(command=cmd, output="Error: command timed out after 30s.", returncode=1)
    except Exception as exc:  # pragma: no cover - unexpected subprocess failure
        return CommandResult(command=cmd, output=f"Error: {exc}", returncode=1)

    combined_output = (completed.stdout or "") + (completed.stderr or "")
    return CommandResult(command=cmd, output=combined_output.strip(), returncode=completed.returncode)

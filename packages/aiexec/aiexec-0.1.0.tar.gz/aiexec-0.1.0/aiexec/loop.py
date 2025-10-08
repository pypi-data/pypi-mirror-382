from __future__ import annotations

import json
import re
import shlex
import time
from dataclasses import dataclass, field
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.text import Text

from .executor import CommandResult, allowed, needs_confirm, safe_run
from .model import query_model


MAX_STEPS = 10
CONSECUTIVE_ERROR_LIMIT = 5
AGENT_INSTRUCTIONS_TEMPLATE = (
    "Reply with exactly one JSON object per message that matches one of these forms:\n"
    '{"type": "shell", "command": "<single-line shell command>"}\n'
    '{"type": "done", "reason": "<short summary>"}\n'
    "Rules:\n"
    "- Work from '{workdir}' in a fresh shell each time; chain related operations with '&&'.\n"
    "- Commands must be one physical line, POSIX-sh compatible, and idempotent.\n"
    "- Never rely on shell history or state from previous commands.\n"
    "- Avoid 'source' or activation scripts; call virtualenv binaries directly (e.g. './venv/bin/pip').\n"
    "- Prefer safe variants: use 'mkdir -p', reuse existing virtualenv paths, avoid '--upgrade' unless necessary.\n"
    "- If a result mentions 'Dry run', assume the command is logically complete and continue with the NEXT distinct step.\n"
    "- Do not repeat commands that were already issued unless the tool explicitly requests a retry.\n"
    "- When you need to inspect files, use non-interactive commands like 'cat', \"sed -n '1,120p' <file>\", or 'tail'. Never launch interactive editors (nano, vi, vim, less, more).\n"
    "Good responses:\n"
    '{"type": "shell", "command": "mkdir -p apiserver"}\n'
    '{"type": "shell", "command": "python -m venv apiserver/venv"}\n'
    '{"type": "shell", "command": "./apiserver/venv/bin/pip install fastapi uvicorn"}\n'
    '{"type": "done", "reason": "Project directory, virtualenv, and dependencies are ready."}\n'
    "Bad responses (do not copy):\n"
    '{"type": "shell", "command": "source apiserver/venv/bin/activate"}  # activation\n'
    '{"type": "shell", "command": "pip install fastapi"}  # not using ./venv/bin/pip\n'
    '{"type": "done", "reason": "DONE: complete"}  # redundant text\n'
    "Typical flow example:\n"
    "1. {\"type\": \"shell\", \"command\": \"mkdir -p apiserver\"}\n"
    "2. {\"type\": \"shell\", \"command\": \"python -m venv apiserver/venv\"}\n"
    "3. {\"type\": \"shell\", \"command\": \"./apiserver/venv/bin/pip install fastapi uvicorn\"}\n"
    "4. {\"type\": \"done\", \"reason\": \"FastAPI project scaffolded with dependencies installed.\"}\n"
    "Only output the JSON object—no prefixes like 'System:' or commentary."
)

FORBIDDEN_COMMAND_PATTERNS = [
    (re.compile(r"\bsource\b"), "Do not use 'source'. Call venv binaries directly (e.g. ./venv/bin/pip)."),
    (re.compile(r"(?:^|[\s;])\.?\s*\S*bin/activate\b"), "Do not activate virtual environments; run ./venv/bin/pip or python instead."),
    (re.compile(r"(?:;|&&)\s*done\b", re.IGNORECASE), "Do not append 'done' inside shell commands; respond with a separate 'DONE: ...' line."),
    (re.compile(r"\b(?:curl|wget)\b[^\n]*\|\s*(?:sh|bash)", re.IGNORECASE), "Do not pipe remote scripts directly into your shell."),
    (re.compile(r"\bchown\s+-R\s+/"), "Do not run recursive chown from the filesystem root."),
    (re.compile(r"\b(?:nano|vi|vim|less|more)\b"), "Avoid interactive editors; use 'cat', 'sed', or 'tail' to view files instead."),
]


@dataclass
class AgentAction:
    type: str
    command: Optional[str] = None
    reason: Optional[str] = None


@dataclass
class SessionState:
    project_dirs: set[str] = field(default_factory=set)
    venv_paths: set[str] = field(default_factory=set)
    packages: Dict[str, set[str]] = field(default_factory=dict)
    steps_since_progress: int = 0
    last_success_command: Optional[str] = None
    last_success_result: Optional[str] = None

    def note_no_progress(self) -> None:
        self.steps_since_progress += 1

    def record_result(self, command: str, result: CommandResult) -> None:
        dry_run = result.skipped and "dry run" in (result.output or "").lower()

        if result.ok or dry_run:
            progressed = self._update_from_command(command)
            if progressed:
                self.steps_since_progress = 0
            else:
                self.steps_since_progress += 1

            self.last_success_command = command
            self.last_success_result = result.output or "(no output)"
            return

        self.note_no_progress()

    def _update_from_command(self, command: str) -> bool:
        progressed = False
        segments = [segment.strip() for segment in command.split("&&") if segment.strip()]

        for segment in segments:
            try:
                tokens = shlex.split(segment)
            except ValueError:
                continue

            if not tokens:
                continue

            head = tokens[0]
            lower_head = head.lower()

            if lower_head == "mkdir":
                for token in tokens[1:]:
                    if token.startswith("-"):
                        continue
                    self.project_dirs.add(token)
                    progressed = True

            if (
                lower_head.startswith("python")
                and len(tokens) >= 4
                and tokens[1] == "-m"
                and tokens[2].lower() == "venv"
            ):
                path = tokens[3]
                self.venv_paths.add(path)
                progressed = True

            pip_path = Path(head)
            if pip_path.name in {"pip", "pip3"} and pip_path.parent.name == "bin" and len(tokens) >= 2:
                subcommand = tokens[1]
                if subcommand == "install":
                    venv_path = str(pip_path.parent.parent)
                    if venv_path and venv_path != ".":
                        self.venv_paths.add(venv_path)
                    packages = [token for token in tokens[2:] if not token.startswith("-")]
                    if packages:
                        pkg_set = self.packages.setdefault(venv_path or "(unknown venv)", set())
                        pkg_set.update(packages)
                        progressed = True

        return progressed

    def summary(self) -> str:
        lines: list[str] = []
        if self.project_dirs:
            lines.append("Project directories: " + ", ".join(sorted(self.project_dirs)))
        if self.venv_paths:
            lines.append("Virtualenvs: " + ", ".join(sorted(self.venv_paths)))
        if self.packages:
            for venv, pkgs in sorted(self.packages.items()):
                if pkgs:
                    lines.append(f"{venv} packages: " + ", ".join(sorted(set(pkgs))))
        if not lines:
            return "(no confirmed progress yet)"
        return "\n".join(lines)

    def preferred_venv(self) -> Optional[str]:
        if not self.venv_paths:
            return None
        return sorted(self.venv_paths)[0]

    def has_package(self, venv: Optional[str], package: str) -> bool:
        target = venv or "(unknown venv)"
        return package in self.packages.get(target, set())

    def recorded_packages(self, venv: Optional[str]) -> set[str]:
        target = venv or "(unknown venv)"
        return set(self.packages.get(target, set()))


def _parse_action(response: str) -> tuple[Optional[AgentAction], Optional[str]]:
    try:
        data = json.loads(response)
    except json.JSONDecodeError as exc:
        return None, f"Response was not valid JSON ({exc.msg})."

    if not isinstance(data, dict):
        return None, "Response JSON must be an object."

    action_type = data.get("type")
    if action_type not in {"shell", "done"}:
        return None, "Field 'type' must be either 'shell' or 'done'."

    if action_type == "shell":
        if set(data.keys()) - {"type", "command"}:
            return None, "Shell actions may only include 'type' and 'command'."
        command = data.get("command")
        if not isinstance(command, str) or not command.strip():
            return None, "Shell actions require a non-empty 'command' string."
        if "\n" in command:
            return None, "Shell command must be a single physical line."
        return AgentAction(type="shell", command=command.strip()), None

    if set(data.keys()) - {"type", "reason"}:
        return None, "Done actions may only include 'type' and 'reason'."
    reason = data.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        return None, "Done actions require a non-empty 'reason' string."
    return AgentAction(type="done", reason=reason.strip()), None


def _extract_install_packages(command: str) -> tuple[Optional[str], list[str]]:
    venv_path: Optional[str] = None
    collected: list[str] = []

    for segment in command.split("&&"):
        segment = segment.strip()
        if not segment:
            continue
        try:
            tokens = shlex.split(segment)
        except ValueError:
            continue
        if not tokens:
            continue
        pip_path = Path(tokens[0])
        is_venv_pip = pip_path.name in {"pip", "pip3"} and pip_path.parent.name == "bin"
        if not (is_venv_pip and len(tokens) >= 2 and tokens[1] == "install"):
            continue
        venv_candidate = str(pip_path.parent.parent)
        if venv_candidate:
            venv_path = venv_candidate
        collected.extend(token for token in tokens[2:] if not token.startswith("-"))

    return venv_path, collected


def _build_prompt(
    *,
    instructions: str,
    goal: str,
    state: SessionState,
    last_command: Optional[str],
    last_result: Optional[CommandResult],
    issue: Optional[str],
    invalid_response: Optional[str],
) -> str:
    sections: list[str] = [instructions, f"Goal: {goal}"]

    progress_summary = state.summary()
    sections.append(f"Confirmed progress:\n{progress_summary}")

    if state.venv_paths:
        sections.append(
            "Known virtualenv paths (reuse when installing packages): " + ", ".join(sorted(state.venv_paths))
        )

    if last_command:
        status = "skipped"
        if last_result:
            if last_result.ok:
                status = "success"
            elif last_result.skipped:
                status = "skipped"
            else:
                status = "error"
        sections.append(f"Last executed command: {last_command}")
        if last_result:
            sections.append(f"Last result status: {status}")
            sections.append(f"Last result output:\n{last_result.output or '(no output)'}")

    if issue:
        sections.append(f"Validation error: {issue}")
        if invalid_response:
            clipped = invalid_response.strip()
            if len(clipped) > 400:
                clipped = clipped[:400] + "…"
            sections.append(f"Your previous invalid response was:\n{clipped}")
        sections.append("Return a corrected JSON object that satisfies the schema.")
    elif state.steps_since_progress >= 3:
        sections.append(
            "No measurable progress detected in the last few attempts. Suggest the next concrete step that advances the goal."
        )

    sections.append("Next action?")
    return "\n\n".join(sections)


def _format_command_result(result: CommandResult) -> Text:
    if result.skipped:
        return Text.from_markup("[yellow]⚠️ Skipped[/yellow]")
    if result.ok:
        return Text.from_markup("[green]✓[/green]")
    return Text.from_markup("[red]✗[/red]")
def run_agent(
    task: Dict[str, Any],
    *,
    assume_yes: bool = False,
    use_sandbox: bool = False,
    verbose: bool = False,
    dry_run: bool = False,
) -> None:
    """
    Execute the agent loop for the provided task.
    """
    console = Console()
    goal = task["goal"]
    model_name = task.get("model", "local")
    permissions = task.get("permissions", [])
    workdir_setting = task.get("workdir", ".")

    console.rule("[bold]aiexec[/bold]")
    console.print(f"[bold cyan]Goal:[/bold cyan] {goal}")

    if dry_run:
        console.print("[yellow]Dry run enabled — commands will not be executed.[/yellow]")
    sandbox_dir: Optional[Path] = None

    with ExitStack() as stack:
        if use_sandbox:
            import tempfile

            sandbox_path = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="aiexec-run-")))
            sandbox_dir = sandbox_path
            console.print(f"[cyan]Sandbox:[/cyan] {sandbox_dir}")
        workdir = sandbox_dir or Path(workdir_setting).expanduser()
        workdir.mkdir(parents=True, exist_ok=True)

        instructions = AGENT_INSTRUCTIONS_TEMPLATE.replace("{workdir}", str(workdir))
        state = SessionState()
        prompt = _build_prompt(
            instructions=instructions,
            goal=goal,
            state=state,
            last_command=None,
            last_result=None,
            issue=None,
            invalid_response=None,
        )
        start_time = time.monotonic()
        step = 0
        executed = 0
        skipped = 0
        errors = 0
        consecutive_errors = 0
        last_executed_command: Optional[str] = None
        last_result: Optional[CommandResult] = None

        def _fail_and_prompt(message: str, *, invalid_response: Optional[str] = None) -> None:
            nonlocal prompt, consecutive_errors, skipped
            console.print(f"[yellow]Warning:[/yellow] {message}")
            state.note_no_progress()
            prompt = _build_prompt(
                instructions=instructions,
                goal=goal,
                state=state,
                last_command=last_executed_command,
                last_result=last_result,
                issue=message,
                invalid_response=invalid_response,
            )
            skipped += 1
            consecutive_errors += 1

        while step < MAX_STEPS:
            step += 1
            console.print(f"\n[bold]Step {step}[/bold] — thinking…")

            raw_response = query_model(prompt, model_name).strip()
            if verbose:
                console.print(f"[dim]Model (raw):[/dim] {raw_response}")

            action, error_message = _parse_action(raw_response)
            if error_message or action is None:
                _fail_and_prompt(error_message or "Invalid response format.", invalid_response=raw_response)
                if consecutive_errors >= CONSECUTIVE_ERROR_LIMIT:
                    console.print("[red]Too many unparsable responses. Stopping.[/red]")
                    break
                continue

            if action.type == "done":
                reason = action.reason or "Goal reported complete."
                console.print(f"[green]DONE:[/green] {reason}")
                break

            command = action.command or ""
            if not verbose:
                console.print(f"[dim]Model proposed command:[/dim] {command}")

            if not allowed(permissions, "shell"):
                _fail_and_prompt("Shell execution not permitted for this task.")
                if consecutive_errors >= CONSECUTIVE_ERROR_LIMIT:
                    console.print("[red]Too many blocked commands. Stopping.[/red]")
                    break
                continue

            if last_executed_command and command == last_executed_command:
                hint = "That command was just executed. Provide the next distinct step that advances the goal."
                preferred_venv = state.preferred_venv()
                if preferred_venv:
                    hint += f" Continue using ./{preferred_venv}/bin/pip for package installs."

                venv_path, packages = _extract_install_packages(command)
                if packages:
                    recorded = state.recorded_packages(venv_path)
                    if recorded:
                        hint += f" Packages already recorded for {venv_path or 'the virtualenv'}: {', '.join(sorted(recorded))}."

                _fail_and_prompt(hint)
                if consecutive_errors >= CONSECUTIVE_ERROR_LIMIT:
                    console.print("[red]Too many immediate repeats. Stopping.[/red]")
                    break
                continue

            is_valid, reason = _validate_command(command)
            if not is_valid:
                _fail_and_prompt(f"Command rejected: {reason}")
                if consecutive_errors >= CONSECUTIVE_ERROR_LIMIT:
                    console.print("[red]Too many policy violations. Stopping.[/red]")
                    break
                continue

            if needs_confirm(command) and not assume_yes:
                _fail_and_prompt(
                    "Command refused due to safety policy. Suggest a safer alternative or wait for manual confirmation."
                )
                console.print(f"[yellow]Warning:[/yellow] {command}")
                console.print("Rerun with --yes to permit dangerous commands.")
                if consecutive_errors >= CONSECUTIVE_ERROR_LIMIT:
                    console.print("[red]Too many unsafe commands. Stopping.[/red]")
                    break
                continue

            console.print(f"[cyan]$ {command}[/cyan]")

            if dry_run:
                console.print("[yellow]Dry run:[/yellow] skipped execution.")
                result = CommandResult(
                    command=command, output="Dry run: command not executed.", returncode=0, skipped=True
                )
            else:
                result = safe_run(command, workdir)

            status = _format_command_result(result)
            if result.output:
                console.print(status, Text(result.output, style="dim"))
            else:
                console.print(status)

            last_executed_command = command
            last_result = result
            state.record_result(command, result)

            if result.skipped:
                skipped += 1
                consecutive_errors = 0
            elif result.ok:
                executed += 1
                consecutive_errors = 0
            else:
                errors += 1
                consecutive_errors += 1

            if consecutive_errors >= CONSECUTIVE_ERROR_LIMIT:
                console.print("[red]Too many errors in a row. Stopping.[/red]")
                break

            prompt = _build_prompt(
                instructions=instructions,
                goal=goal,
                state=state,
                last_command=last_executed_command,
                last_result=last_result,
                issue=None,
                invalid_response=None,
            )
        else:
            console.print(f"[yellow]Warning:[/yellow] Step limit of {MAX_STEPS} reached. Stopping.")

        elapsed = time.monotonic() - start_time
        console.rule()
        console.print("[bold]Task Summary:[/bold]")
        console.print(f"[green]✓ {executed} commands executed successfully[/green]")
        console.print(f"[yellow]⚠️ {skipped} skipped[/yellow]")
        console.print(f"[red]✗ {errors} errors[/red]")
        console.print(f"[cyan]⏱ {elapsed:.1f}s elapsed[/cyan]")
        console.print("[blue]Progress tracked:[/blue]\n" + state.summary())
def _validate_command(command: str) -> tuple[bool, Optional[str]]:
    for pattern, message in FORBIDDEN_COMMAND_PATTERNS:
        if pattern.search(command):
            return False, message

    segments = [segment.strip() for segment in command.split("&&")]
    for segment in segments:
        if not segment:
            continue
        try:
            tokens = shlex.split(segment)
        except ValueError:
            return False, "Command contains unmatched quotes; provide a valid single-line shell command."
        if not tokens:
            continue
        first = tokens[0]
        lower_first = first.lower()

        if lower_first == "mkdir":
            flags = [token for token in tokens[1:] if token.startswith("-")]
            if not any(flag in {"-p", "--parents"} for flag in flags):
                return False, "Use 'mkdir -p <dir>' for idempotence."

        pip_path = Path(first)
        is_venv_pip = pip_path.name in {"pip", "pip3"} and pip_path.parent.name == "bin"
        if is_venv_pip and len(tokens) >= 2 and tokens[1] == "install":
            if any(flag in {"--upgrade", "-U"} for flag in tokens[2:]):
                return False, "Avoid '--upgrade' for deterministic installs; pin package versions if necessary."
            continue

        if lower_first in {"pip", "pip3"}:
            return False, "Run pip via the virtualenv binary (e.g. ./apiserver/venv/bin/pip install ...)."

        if lower_first.startswith("pip"):
            return False, "Run pip via the virtualenv binary (e.g. ./apiserver/venv/bin/pip install ...)."

        if (
            lower_first.startswith("python")
            and len(tokens) >= 3
            and tokens[1] == "-m"
            and tokens[2].lower() == "pip"
        ):
            return False, "Use the virtualenv pip binary directly instead of 'python -m pip'."

    return True, None

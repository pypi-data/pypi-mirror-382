from pathlib import Path
from typing import Optional

import typer
from rich import print

from .loop import run_agent
from .parser import load_ai_file
from .templates import create_template, discover_scripts
from .model import diagnose_environment

app = typer.Typer(add_completion=False, help="Run natural-language .ai automation scripts.")


@app.command()
def run(
    file: Path = typer.Argument(..., exists=True, readable=True, resolve_path=True, help="Path to the .ai file."),
    yes: bool = typer.Option(False, "--yes", help="Auto-confirm dangerous commands."),
    model: Optional[str] = typer.Option(None, "--model", help="Override the model defined in the .ai file."),
    sandbox: bool = typer.Option(False, "--sandbox", help="Execute commands in an isolated temporary directory."),
    verbose: bool = typer.Option(False, "--verbose", help="Print raw model responses."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print commands without executing them."),
):
    """
    Execute a .ai YAML file with an agentic Reason–Act–Verify loop.
    """
    task = load_ai_file(str(file))
    if model:
        task["model"] = model

    run_agent(
        task,
        assume_yes=yes,
        use_sandbox=sandbox,
        verbose=verbose,
        dry_run=dry_run,
    )


@app.command()
def init(
    name: str = typer.Argument(..., help="Name of the new .ai script (without extension)."),
    directory: Path = typer.Option(
        ".", "--dir", "-d", help="Directory where the template will be written.", resolve_path=True
    ),
    model: str = typer.Option("local", "--model", help="Model name to include in the template."),
):
    """
    Generate a starter .ai automation file in the target directory.
    """
    target = directory / f"{name}.ai"
    created = create_template(target, model=model)

    if created:
        print(f"[green]Created template:[/green] {target}")
    else:
        print(f"[yellow]Skipped:[/yellow] {target} already exists.")


@app.command("list")
def list_scripts(
    directory: Path = typer.Option(
        ".", "--dir", "-d", help="Directory to scan for .ai scripts.", resolve_path=True
    ),
):
    """
    List .ai automation scripts in the given directory.
    """
    scripts = discover_scripts(directory)
    if not scripts:
        print("[yellow]No .ai scripts found.[/yellow]")
        raise typer.Exit(0)

    for script in scripts:
        print(f"- {script}")


@app.command()
def doctor():
    """
    Diagnose common setup issues.
    """
    messages = diagnose_environment()
    for level, message in messages:
        if level == "ok":
            print(f"[green]✓ {message}[/green]")
        elif level == "warn":
            print(f"[yellow]! {message}[/yellow]")
        else:
            print(f"[red]✗ {message}[/red]")


if __name__ == "__main__":
    app()

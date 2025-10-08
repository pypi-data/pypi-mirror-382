# aiexec

Run natural-language `.ai` automation scripts with a local, safe, agentic CLI loop.

## Quick Install

| Method | Command |
| --- | --- |
| **pipx (recommended)** | `pipx install aiexec` |
| **pip** | `python -m pip install aiexec` |
| **Source** | `pip install -e .` (from a cloned repo) |

### One-line bootstrap (macOS/Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/your-org/aiexec/main/install/install-aiexec.sh | bash
```

### One-line bootstrap (Windows PowerShell)

```powershell
irm https://raw.githubusercontent.com/your-org/aiexec/main/install/install-aiexec.ps1 | iex
```

## Usage

Run the provided example task:

```bash
aiexec run examples/setup_fastapi.ai --dry-run
```

- `--yes` auto-confirms dangerous commands (e.g., `rm -rf`); omit to require confirmation.
- `--sandbox` executes inside a temporary directory instead of your current working tree.
- `--verbose` prints raw model responses.
- `--dry-run` shows proposed commands without executing them.

Other helpful commands:

```bash
aiexec init my_task         # create my_task.ai template
aiexec list                 # list .ai files in the current directory
aiexec doctor               # check for Ollama/Hugging Face setup issues
```

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/download) with the `llama3:instruct` model (`ollama pull llama3:instruct`)
- Optional: `HUGGINGFACE_API_TOKEN` environment variable for Hugging Face models (`--model hf:<repo>`).

## Development

Format and lint (optional):

```bash
pip install black ruff
black aiexec
ruff check aiexec
```

Run the unit-less sanity check:

```bash
python -m compileall aiexec
```

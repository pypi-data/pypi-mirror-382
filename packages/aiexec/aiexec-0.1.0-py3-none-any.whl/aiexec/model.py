from __future__ import annotations

import json
import os
import subprocess
from typing import List, Optional, Tuple
from urllib import error, request


DEFAULT_LOCAL_MODEL = "llama3:instruct"

SYSTEM_PROMPT = (
    "You are a CLI automation agent that must respond with EXACTLY one JSON object per message matching this schema:\n"
    '{"type": "shell", "command": "<single-line shell command>"}\n'
    '{"type": "done", "reason": "<short summary>"}\n'
    "Rules:\n"
    "- Each command runs in a fresh shell from the provided working directory; include any required `cd` or setup in the same command using '&&'.\n"
    "- Commands must be POSIX sh-compatible, single-line, and idempotent (use 'mkdir -p', avoid '--upgrade' unless required).\n"
    "- Never rely on previous shell state or history.\n"
    "- Do NOT use 'source' or activation scripts; call virtualenv binaries directly (e.g. './venv/bin/pip').\n"
    "- If a result mentions 'Dry run', assume the command is logically complete and move on to the NEXT distinct step.\n"
    "- Do not repeat commands unless explicitly asked to retry them.\n"
    "- When you need to show file contents, use non-interactive commands like 'cat', \"sed -n '1,120p' <file>\", or 'tail'; never launch interactive editors (nano, vi, vim, less, more).\n"
    "Good responses:\n"
    '{"type": "shell", "command": "mkdir -p apiserver"}\n'
    '{"type": "shell", "command": "python -m venv apiserver/venv"}\n'
    '{"type": "shell", "command": "./apiserver/venv/bin/pip install fastapi uvicorn"}\n'
    '{"type": "done", "reason": "Project directory, virtualenv, and dependencies are ready."}\n'
    "Bad responses (never emulate):\n"
    '{"type": "shell", "command": "source venv/bin/activate"}\n'
    '{"type": "shell", "command": "pip install fastapi"}\n'
    '{"type": "done", "reason": "DONE: tasks complete"}\n'
    "Typical multi-step flow:\n"
    "1. {\"type\": \"shell\", \"command\": \"mkdir -p apiserver\"}\n"
    "2. {\"type\": \"shell\", \"command\": \"python -m venv apiserver/venv\"}\n"
    "3. {\"type\": \"shell\", \"command\": \"./apiserver/venv/bin/pip install fastapi uvicorn\"}\n"
    "4. {\"type\": \"done\", \"reason\": \"FastAPI project scaffolded with dependencies installed.\"}\n"
    "Output only the JSON object—no 'System:'/'Assistant:' prefixes or commentary."
)


def _ollama_host() -> str:
    host = os.getenv("OLLAMA_HOST", "127.0.0.1:11434")
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"
    return host.rstrip("/")


def _query_ollama_http(user_prompt: str, model_name: str) -> str:
    url = f"{_ollama_host()}/api/generate"
    body = {
        "model": model_name,
        "system": SYSTEM_PROMPT,
        "prompt": user_prompt,
        "stream": False,
        "options": {"temperature": 0.0, "top_p": 0.9},
    }
    data = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with request.urlopen(req, timeout=60) as resp:
            payload = resp.read()
    except error.HTTPError as http_err:
        detail = http_err.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Ollama HTTP {http_err.code}: {detail}") from http_err
    except error.URLError as url_err:
        raise RuntimeError(f"Ollama HTTP request failed: {url_err.reason}") from url_err
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Ollama HTTP request failed: {exc}") from exc

    try:
        body = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Ollama returned invalid JSON: {exc}") from exc

    if isinstance(body, dict) and body.get("error"):
        raise RuntimeError(f"Ollama error: {body['error']}")

    if isinstance(body, dict) and "response" in body:
        return body["response"].strip()

    raise RuntimeError("Unexpected Ollama response format.")


def _have_ollama() -> bool:
    try:
        subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        return True
    except Exception:
        return False


def _ollama_has_model(name: str) -> bool:
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return False
        target = name.lower()
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            first = line.split()[0].lower()
            if first == target:
                return True
            if first.split(":", 1)[0] == target:
                return True
        return False
    except Exception:
        return False


def query_model(user_prompt: str, model: str) -> str:
    """
    Dispatch model queries between local (Ollama) and Hugging Face endpoints.
    """
    target = model or "local"
    if target == "local":
        return query_local(user_prompt)
    if target.startswith("hf:"):
        return query_huggingface(user_prompt, target.partition(":")[2])

    # Treat any other target as an Ollama model name.
    return query_local(user_prompt, model_name=target)


def query_local(user_prompt: str, model_name: str | None = None) -> str:
    if not _have_ollama():
        raise RuntimeError(
            "Ollama not found. Install from https://ollama.com and run `ollama pull "
            f"{model_name or DEFAULT_LOCAL_MODEL}`."
        )

    name = model_name or DEFAULT_LOCAL_MODEL
    http_error: Optional[RuntimeError] = None
    try:
        return _query_ollama_http(user_prompt, name)
    except RuntimeError as exc:
        http_error = exc

    payload = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
    process = subprocess.run(
        ["ollama", "run", name],
        input=payload,
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        message = process.stderr.strip() or process.stdout.strip() or "Ollama failed to produce a response."
        if http_error:
            message = f"{message} (HTTP fallback error: {http_error})"
        raise RuntimeError(message)
    return process.stdout.strip()


def query_huggingface(user_prompt: str, model_repo: str) -> str:
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        raise RuntimeError("Set HUGGINGFACE_API_TOKEN to use Hugging Face inference.")

    api_url = f"https://api-inference.huggingface.co/models/{model_repo}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"inputs": f"{SYSTEM_PROMPT}\n\n{user_prompt}", "parameters": {"max_new_tokens": 200}}

    req = request.Request(api_url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")

    try:
        with request.urlopen(req, timeout=30) as resp:
            payload = resp.read()
    except error.HTTPError as http_err:
        raise RuntimeError(f"Hugging Face error: {http_err.read().decode('utf-8', errors='ignore')}") from http_err
    except Exception as exc:
        raise RuntimeError(f"Hugging Face request failed: {exc}") from exc

    try:
        body = json.loads(payload)
    except json.JSONDecodeError:
        return payload.decode("utf-8", errors="ignore").strip()

    if isinstance(body, dict) and "error" in body:
        raise RuntimeError(f"Hugging Face error: {body['error']}")

    if isinstance(body, list) and body and isinstance(body[0], dict) and "generated_text" in body[0]:
        return body[0]["generated_text"].strip()

    if isinstance(body, dict) and "generated_text" in body:
        return body["generated_text"].strip()

    return json.dumps(body)


def diagnose_environment() -> List[Tuple[str, str]]:
    """
    Return a list of (level, message) tuples describing environment status.
    """
    messages: List[Tuple[str, str]] = []

    if _have_ollama():
        messages.append(("ok", "Ollama detected."))
        if not _ollama_has_model(DEFAULT_LOCAL_MODEL):
            messages.append(
                (
                    "warn",
                    f"Default model '{DEFAULT_LOCAL_MODEL}' is missing. Run `ollama pull {DEFAULT_LOCAL_MODEL}`.",
                )
            )
    else:
        messages.append(
            (
                "error",
                "Ollama not found. Install from https://ollama.com and pull the llama3:instruct model for best results.",
            )
        )

    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if token:
        messages.append(("ok", "Hugging Face token detected in environment."))
    else:
        messages.append(("warn", "Hugging Face token missing (optional, required only for HF models)."))

    return messages

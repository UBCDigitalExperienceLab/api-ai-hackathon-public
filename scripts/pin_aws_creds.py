"""Copy current AWS env vars into the local venv activate scripts.

Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN
in this terminal first (Workshop Studio CLI credentials), then run:

    python scripts/pin_aws_creds.py

Later `activate` calls in this venv reuse those values. Never commit
.venv or the activate scripts after they contain credentials.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"
REQUIRED = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN")
BEGIN = ">>> workshop-aws-creds"
END = "<<< workshop-aws-creds"


def _require_values() -> dict[str, str]:
    missing = [name for name in REQUIRED if not os.environ.get(name)]
    if missing:
        print(
            "AWS credentials are not set in this terminal. "
            "Export AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and "
            "AWS_SESSION_TOKEN from Workshop Studio, then run this script again."
        )
        print("Missing: " + ", ".join(missing))
        sys.exit(1)
    return {name: os.environ[name] for name in REQUIRED}


def _replace_block(text: str, block: str) -> str:
    start = text.find(BEGIN)
    stop = text.find(END)
    if start != -1 and stop != -1:
        stop += len(END)
        while stop < len(text) and text[stop] in "\r\n":
            stop += 1
        return text[:start].rstrip("\n") + "\n\n" + block + text[stop:]
    if not text.endswith("\n"):
        text += "\n"
    return text + "\n" + block


def _unix_block(values: dict[str, str]) -> str:
    lines = [f"# {BEGIN}"]
    for name, value in values.items():
        escaped = value.replace("\\", "\\\\").replace("'", "'\"'\"'")
        lines.append(f"export {name}='{escaped}'")
    lines.append(f"# {END}\n")
    return "\n".join(lines)


def _powershell_block(values: dict[str, str]) -> str:
    lines = [f"# {BEGIN}"]
    for name, value in values.items():
        escaped = value.replace("'", "''")
        lines.append(f"$env:{name} = '{escaped}'")
    lines.append(f"# {END}\n")
    return "\n".join(lines)


def _write(path: Path, block: str) -> None:
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(_replace_block(original, block), encoding="utf-8")
    print(f"Updated {path.relative_to(ROOT)}")


def main() -> None:
    if not VENV.is_dir():
        print("No .venv directory. Run `uv venv` and `uv sync` first.")
        sys.exit(1)
    values = _require_values()
    written = False
    unix = VENV / "bin" / "activate"
    if unix.exists():
        _write(unix, _unix_block(values))
        written = True
    powershell = VENV / "Scripts" / "Activate.ps1"
    if powershell.exists():
        _write(powershell, _powershell_block(values))
        written = True
    if not written:
        print("Could not find a venv activate script under .venv.")
        sys.exit(1)
    print("Credentials will load the next time you activate this venv.")
    print("Do not commit .venv.")


if __name__ == "__main__":
    main()

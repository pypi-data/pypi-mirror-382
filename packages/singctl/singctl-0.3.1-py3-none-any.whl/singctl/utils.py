from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess, run
from typing import Any

from httpx import HTTPStatusError, RequestError, Response, get
from typer import secho

from .exceptions import SingctlError


def error_print(message: str) -> None:
    secho(message, err=True, fg="red")


def success_print(message: str) -> None:
    secho(message, fg="green")


def download_file(url: str, path: Path) -> None:
    try:
        res: Response = get(url)
        res.raise_for_status()
    except RequestError as e:
        raise SingctlError(f"An error occurred while requesting {e.request.url!r}")
    except HTTPStatusError as e:
        raise SingctlError(f"Error response {e.response.status_code} while requesting {e.request.url!r}")
    else:
        with path.open("wb") as f:
            for chunk in res.iter_bytes():
                f.write(chunk)


def eval_command(command: list[str], **kwargs: Any) -> str:
    try:
        process: CompletedProcess[str] = run(
            command, capture_output=True, check=True, encoding="utf-8", errors="replace", text=True, **kwargs
        )
    except FileNotFoundError:
        raise SingctlError("Command not found")
    except CalledProcessError as e:
        raise SingctlError(f"Command exited with exit code {e.returncode}: {e.stderr}".strip())
    else:
        return process.stdout.strip()

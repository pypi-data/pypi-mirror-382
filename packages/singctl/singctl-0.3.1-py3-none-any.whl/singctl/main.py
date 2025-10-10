import platform
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from tinydb import Query, TinyDB
from tinydb.queries import QueryInstance
from tinydb.table import Document
from typer import Argument, Context, Exit, Typer, echo, get_app_dir

from .exceptions import SingctlError
from .utils import download_file, error_print, eval_command, success_print

APP_NAME = "singctl"

app = Typer(name=APP_NAME)


@dataclass
class State:
    app_dir: Path
    db: TinyDB
    query: Query
    profiles_dir: Path
    nssm_path: Path
    singbox_path: Path


@app.callback()
def main_callback(ctx: Context) -> None:
    os_type: str = platform.system()
    if os_type != "Windows":
        error_print(f"{APP_NAME} only support Windows")
        raise Exit(1)

    app_dir = Path(get_app_dir(APP_NAME))
    app_dir.mkdir(exist_ok=True)

    db_path: Path = app_dir / "db.json"
    db = TinyDB(db_path)
    query = Query()

    profiles_dir: Path = app_dir / "profiles"
    profiles_dir.mkdir(exist_ok=True)

    nssm_path: Path = app_dir / "nssm.exe"
    singbox_path: Path = app_dir / "sing-box.exe"

    state = State(
        app_dir=app_dir, db=db, query=query, profiles_dir=profiles_dir, nssm_path=nssm_path, singbox_path=singbox_path
    )
    ctx.obj = state


@app.command("add", help="Download profile from URL to path")
def add(
    ctx: Context,
    name: Annotated[str, Argument(help="Profile name")],
    url: Annotated[str, Argument(help="Remote URL")],
) -> None:
    state: State = ctx.obj

    if state.db.contains(state.query.name == name):
        error_print("Profile already exists")
        raise Exit(1)

    profile_path: Path = state.profiles_dir / name

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Downloading...", total=None)
            download_file(url, profile_path)
    except SingctlError as e:
        error_print(f"Failed to download profile: {e}")
        raise Exit(2)
    else:
        state.db.insert({"name": name, "url": url, "path": str(profile_path), "active": False})
        success_print("Add profile completed")


@app.command("remove", help="Remove profile")
def remove(ctx: Context, name: Annotated[str, Argument(help="Profile name")]) -> None:
    state: State = ctx.obj

    cond: QueryInstance = state.query.name == name

    if not state.db.contains(cond):
        error_print("Profile not found")
        raise Exit(1)

    profile: Document = state.db.search(cond)[0]

    state.db.remove(cond)
    Path(profile["path"]).unlink()

    success_print("Remove profile completed")


@app.command("update", help="Update profile.")
def update(ctx: Context, name: Annotated[str, Argument(help="Profile name")]) -> None:
    state: State = ctx.obj

    cond: QueryInstance = state.query.name == name

    if not state.db.contains(cond):
        error_print("Profile not found")
        raise Exit(1)

    profile: Document = state.db.search(cond)[0]

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Downloading...", total=None)
            download_file(profile["url"], Path(profile["path"]))
    except SingctlError as e:
        error_print(f"Failed to update profile: {e}")
        raise Exit(2)
    else:
        success_print("Update profile completed")


@app.command("list", help="Show all profiles info")
def list(ctx: Context) -> None:
    state: State = ctx.obj

    table = Table("Name", "URL", "Path", "Active")
    for profile in state.db.all():
        table.add_row(profile["name"], profile["url"], profile["path"], str(profile["active"]))
    console = Console()
    console.print(table)


@app.command("install", help="Install sing-box NSSM service")
def install(ctx: Context) -> None:
    state: State = ctx.obj

    bin_dir: Path = Path(__file__).parent / "bin"
    nssm_path: Path = bin_dir / "nssm.exe"
    singbox_path: Path = bin_dir / "sing-box.exe"

    if not state.nssm_path.exists():
        shutil.copy2(nssm_path, state.nssm_path)
    if not state.singbox_path.exists():
        shutil.copy2(singbox_path, state.singbox_path)

    try:
        eval_command([str(state.nssm_path), "install", "sing-box", str(state.singbox_path)], cwd=state.app_dir)
    except SingctlError as e:
        error_print(str(e))
        raise Exit(2)
    else:
        success_print("Install service completed")


@app.command("uninstall", help="Uninstall sing-box NSSM service")
def uninstall(ctx: Context) -> None:
    state: State = ctx.obj

    try:
        eval_command([str(state.nssm_path), "remove", "sing-box", "confirm"], cwd=state.app_dir)
    except SingctlError as e:
        error_print(str(e))
        raise Exit(2)
    else:
        success_print("Uninstall service completed")


@app.command("start", help="Start sing-box NSSM service")
def start(ctx: Context, name: Annotated[str, Argument()]) -> None:
    state: State = ctx.obj

    cond: QueryInstance = state.query.name == name

    if not state.db.contains(cond):
        error_print("Profile not found")
        raise Exit(1)

    profile: Document = state.db.search(cond)[0]

    try:
        eval_command(
            [str(state.nssm_path), "set", "sing-box", "AppParameters", f"run -c {profile['path']}"], cwd=state.app_dir
        )
        eval_command([str(state.nssm_path), "start", "sing-box"], cwd=state.app_dir)
    except SingctlError as e:
        error_print(str(e))
        raise Exit(2)
    else:
        state.db.update({"active": True}, cond)
        success_print("Start service completed")


@app.command("stop", help="Stop sing-box NSSM service")
def stop(ctx: Context) -> None:
    state: State = ctx.obj

    cond: QueryInstance = state.query.active == True  # noqa: E712

    try:
        eval_command([str(state.nssm_path), "stop", "sing-box"], cwd=state.app_dir)
    except SingctlError as e:
        error_print(str(e))
        raise Exit(2)
    else:
        state.db.update({"active": False}, cond)
        success_print("Stop service completed")


@app.command("restart", help="Restart sing-box NSSM service")
def restart(ctx: Context) -> None:
    state: State = ctx.obj

    try:
        eval_command([str(state.nssm_path), "restart", "sing-box"], cwd=state.app_dir)
    except SingctlError as e:
        error_print(str(e))
        raise Exit(2)
    else:
        success_print("Restart service completed")


@app.command("status", help="Check status of sing-box NSSM service")
def status(ctx: Context) -> None:
    state: State = ctx.obj

    try:
        cond: QueryInstance = state.query.active == True  # noqa: E712
        profile: Document = state.db.search(cond)[0]
    except IndexError:
        active_profile_name: str | None = None
    else:
        active_profile_name: str | None = profile["name"]

    try:
        result: str = eval_command([str(state.nssm_path), "status", "sing-box"], cwd=state.app_dir)
    except SingctlError as e:
        error_print(str(e))
        raise Exit(2)
    else:
        echo(f"Profile name: {active_profile_name}")
        echo(f"Service status: {result}")

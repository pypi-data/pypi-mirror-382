from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, assert_never

import utilities.click
from click import Choice, option
from tomlkit import TOMLDocument, parse
from tomlkit.items import Table
from utilities.atomicwrites import writer
from utilities.functions import get_class_name
from utilities.hashlib import md5_hash
from utilities.pathlib import get_repo_root
from utilities.typing import get_literal_elements
from utilities.version import Version, parse_version
from utilities.whenever import get_now_local, to_zoned_date_time
from xdg_base_dirs import xdg_cache_home

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from whenever import DateTimeDelta

type Mode = Literal["pyproject", "bumpversion"]
DEFAULT_MODE: Mode = "pyproject"
mode_option = option(
    "--mode",
    type=Choice(get_literal_elements(Mode), case_sensitive=False),
    default=DEFAULT_MODE,
    show_default=True,
)
run_every_option = option(
    "--run-every", type=utilities.click.DateTimeDelta(), default=None, show_default=True
)


def get_version(source: Mode | Path | str | bytes | TOMLDocument, /) -> Version:
    """Get the `[tool.bumpversion]` version from a TOML file."""
    match source:
        case "pyproject" | "bumpversion" as mode:
            return get_version(get_toml_path(mode))
        case Path() as path:
            return get_version(path.read_text())
        case str() | bytes() as text:
            return get_version(parse(text))
        case TOMLDocument() as doc:
            try:
                tool = doc["tool"]
            except KeyError:
                msg = "Key 'tool' does not exist"
                raise GetVersionError(msg) from None
            if not isinstance(tool, Table):
                msg = "`tool` is not a Table"
                raise GetVersionError(msg)
            try:
                bumpversion = tool["bumpversion"]
            except KeyError:
                msg = "Key 'bumpversion' does not exist"
                raise GetVersionError(msg) from None
            if not isinstance(bumpversion, Table):
                msg = "`bumpversion` is not a Table"
                raise GetVersionError(msg)
            try:
                version = bumpversion["current_version"]
            except KeyError:
                msg = "Key 'current_version' does not exist"
                raise GetVersionError(msg) from None
            if not isinstance(version, str):
                msg = f"`version` is not a string; got {get_class_name(version)!r}"
                raise GetVersionError(msg)
            return parse_version(version)
        case never:  # pyright: ignore[reportUnnecessaryComparison]
            assert_never(never)


class GetVersionError(Exception): ...


def get_toml_path(mode: Mode = DEFAULT_MODE, /) -> Path:
    """Get the path of the TOML file with the version."""
    match mode:
        case "pyproject":
            return Path("pyproject.toml")
        case "bumpversion":
            return Path(".bumpversion.toml")
        case never:  # pyright: ignore[reportUnnecessaryComparison]
            assert_never(never)


def run_all(iterator: Iterator[bool], /) -> bool:
    """Run all of a set of jobs."""
    return all(list(iterator))


def throttled_run[**P](
    name: str,
    run_every: DateTimeDelta | None,
    func: Callable[P, bool],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> bool:
    """Throttled run."""
    hash_ = md5_hash(get_repo_root())
    path = xdg_cache_home().joinpath("pre-commit-hooks", name, hash_)
    if run_every is not None:
        min_date_time = get_now_local() - run_every
        try:
            text = path.read_text()
        except FileNotFoundError:
            pass
        else:
            try:
                last_run = to_zoned_date_time(text.strip("\n"))
            except ValueError:
                pass
            else:
                if min_date_time <= last_run:
                    return True
    try:
        return func(*args, **kwargs)
    finally:
        _ = write_text(path, str(get_now_local()))


def write_text(path: Path, text: str, /) -> Literal[False]:
    """Write text to a file."""
    with writer(path, overwrite=True) as temp:
        _ = temp.write_text(text)
    return False


__all__ = [
    "DEFAULT_MODE",
    "Mode",
    "get_toml_path",
    "get_version",
    "mode_option",
    "run_all",
    "run_every_option",
    "throttled_run",
    "write_text",
]

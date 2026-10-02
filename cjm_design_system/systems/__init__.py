"""The design systems this library ships as DATA (ruling a439c226): one
directory per system under this package — `tokens.json` (schema v1) and
`fonts/` (the OFL files its tokens name, with their licence). What only a
consumer reads lives with that consumer: the Qt kit keeps each system's QSS
templates and painted widgets under its own `systems/<slug>/` (design
0858bbd0).

    available()          -> ["classical", "netrunner"]
    locate("netrunner")  -> the system's directory
    locate("/path/to/mysystem/tokens.json") -> that file's directory

Custom systems come AFTER the gallery (abb6360d); a path-valued system is
how one is tried before it is vendored."""

from pathlib import Path
from typing import List, Union

SYSTEMS_DIR = Path(__file__).parent


def available() -> List[str]:
    """Every vendored system slug (a directory carrying a tokens.json)."""
    return sorted(p.parent.name for p in SYSTEMS_DIR.glob("*/tokens.json"))


def locate(system: Union[str, Path]) -> Path:
    """The directory of a system: a vendored slug, a directory holding a
    tokens.json, or a tokens.json path. Raises KeyError naming the slugs
    available when nothing matches."""
    p = Path(system)
    if p.suffix == ".json" and p.is_file():
        return p.parent
    if p.is_dir() and (p / "tokens.json").is_file():
        return p
    if (SYSTEMS_DIR / str(system) / "tokens.json").is_file():
        return SYSTEMS_DIR / str(system)
    raise KeyError(f"no design system {system!r} — vendored: {available()}; "
                   "or pass a directory holding tokens.json")


def tokens_path(system: Union[str, Path]) -> Path:
    return locate(system) / "tokens.json"

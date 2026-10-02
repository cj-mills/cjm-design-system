"""Build the static web projections of a design system: the CSS
custom-properties layer (`tokens.to_css`, the web consumer 8079ae0f), after
the schema check. The Qt projections (QSS per mode, recolored icons) build
from the kit (`python -m cjm_substrate_qt_kit.tools.build`).

    python -m cjm_design_system.tools.build netrunner -o build/
    python -m cjm_design_system.tools.build path/to/mysystem/tokens.json --check
"""

import argparse
from pathlib import Path

from .. import systems, tokens as T


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m cjm_design_system.tools.build")
    ap.add_argument("system", help="a vendored slug or a tokens.json path")
    ap.add_argument("-o", "--out", default="build")
    ap.add_argument("--check", action="store_true", help="validate only; write nothing")
    a = ap.parse_args(argv)
    path = systems.tokens_path(a.system)
    tok = T.load(path)
    T.check(tok, str(path))
    if a.check:
        print(f"{T.slug(tok)}: schema v{T.SCHEMA_VERSION} OK — modes {T.modes(tok)}")
        return 0
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    css = out / f"{T.slug(tok)}.css"
    css.write_text(T.to_css(tok), encoding="utf-8")
    print(f"wrote {css}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

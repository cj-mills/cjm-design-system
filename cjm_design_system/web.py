"""The web projections of a design system beyond the CSS variable layer (design
0858bbd0 (3) + (4), leg C of the theme half of 8079ae0f): a Quarto / Bootstrap
theme file per mode and the system's fonts as woff2 split by unicode range.

A Quarto site switches light / dark by swapping whole stylesheets, so a theme is
one file PER MODE: `scss:defaults` sets Bootstrap's variables as LITERAL values
from `tokens.resolve` (Bootstrap runs colour functions on them at compile time, so
a CSS variable cannot stand there), and `scss:rules` carries the font faces, that
mode's variable block (`tokens.to_css(mode=...)`) and the per-level heading
weights the type scale names. Nothing here types a colour or a font name: every
value is read from the tokens or from the font files themselves.

The fonts: each TTF a system's `fonts.files` globs name is subset into up to three
woff2 files the way Google Fonts serves them -- Latin, Latin Extended, and the rest
of what the font covers -- so no glyph is lost and a reader downloads only the
ranges a page uses. Family, style and weight range are read from each file (the
variable fonts' weight axis, else the OS/2 weight class), never typed. fontTools
and brotli are the `web` extra; they load only when fonts are converted.

    theme_scss(tokens, "light", faces_css)   -> the Quarto theme file for one mode
    font_files(tokens, system_dir)           -> the TTF / OTF files the tokens name
    web_fonts(files, out_dir, "fonts/x/")    -> {css, files, faces, sources, unmatched}
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from . import tokens as T

# Google Fonts' own unicode-range lists for its `latin` and `latin-ext` subsets
LATIN_RANGES = ("U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, "
                "U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD")
LATIN_EXT_RANGES = ("U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, "
                    "U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, "
                    "U+2C60-2C7F, U+A720-A7FF")
# Quarto's callouts read their own colour variables (not Bootstrap's state colours): each
# callout takes a state role -- first values, settled by the light / dark visual review
CALLOUT_ROLES = (("note", "info"), ("tip", "ok"), ("important", "danger"),
                 ("warning", "warn"), ("caution", "note"))
_MANIFEST = ".web-fonts.json"


def parse_ranges(spec: str) -> Set[int]:
    """A CSS unicode-range list ("U+0000-00FF, U+0131") -> the code points it names."""
    out: Set[int] = set()
    for part in spec.split(","):
        part = part.strip().upper().removeprefix("U+")
        if not part:
            continue
        lo, _, hi = part.partition("-")
        out.update(range(int(lo, 16), int(hi or lo, 16) + 1))
    return out


def format_ranges(points: Iterable[int]) -> str:
    """Code points -> the shortest CSS unicode-range list naming exactly them."""
    pts = sorted(set(points))
    runs: List[Tuple[int, int]] = []
    for p in pts:
        if runs and p == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], p)
        else:
            runs.append((p, p))
    return ", ".join(f"U+{a:04X}" if a == b else f"U+{a:04X}-{b:04X}" for a, b in runs)


# ---- the Bootstrap / Quarto theme ---------------------------------------------

def _px(v: Any) -> str:
    return f"{float(v):g}px"


def _rem(px: Any, base: Any) -> str:
    return f"{round(float(px) / float(base), 4):g}rem"


def _family(name: str, generic: Optional[str]) -> str:
    return f'"{name}"' + (f", {generic}" if generic else "")


def bootstrap_defaults(
    tokens: Dict[str, Any],     # A checked schema-v1 system
    mode: str,                  # One of the system's own modes
    generics: Optional[Dict[str, str]] = None,  # {family: CSS generic family} read from the font files
) -> str:  # The `scss:defaults` body: Bootstrap / Quarto variables as literal values
    """Bootstrap's variables for one mode, every value read from `resolve(tokens, mode)`:
    the page colours, the accent as primary (and its text tone as the link colour), the six
    state roles onto Bootstrap's state colours and Quarto's callouts, the font families,
    the base size and heading scale, the radii and the spacer; Bootstrap's grey scale on the
    neutral ramp, the chrome (navbar, footer) as the system draws it, and code on its panel
    vocabulary (amendment of 0858bbd0 after the first visual review). An empty mono slot
    leaves Bootstrap's monospace stack in place (no code roles in the tokens)."""
    v = T.resolve(tokens, mode)
    g = generics or {}
    base = tokens["fonts"]["body"]["size"]
    neutral = tokens["ramps"]["neutral"]
    rows: List[Tuple[str, str]] = [
        ("body-bg", v["bg"]), ("body-color", v["text"]),
        ("body-secondary-color", v["muted_solid"]), ("border-color", v["divider_solid"]),
        ("primary", v["accent"]), ("secondary", v["muted_solid"]),
        ("success", v["ok"]), ("info", v["info"]), ("warning", v["warn"]), ("danger", v["danger"]),
        ("light", v["surface"]), ("dark", neutral[8]),
        ("link-color", v["accent_text"]),
    ]
    # Bootstrap's grey scale on the neutral ramp, step 100 nearest the page in EITHER mode: the
    # ramp reversed where the page is darker than its ink (relative luminance, never the mode's
    # name), so every grey Bootstrap or Quarto still derives on its own (progress bars, the code
    # block's default, table stripes) stays on the system
    lum = [sum(w * c for w, c in zip((.2126, .7152, .0722), T._rgb(v[k]))) for k in ("bg", "text")]
    grays = neutral[::-1] if lum[0] < lum[1] else neutral
    rows += [(f"gray-{(i + 1) * 100}", c) for i, c in enumerate(grays)]
    # The chrome as the system draws it (the gallery's title / menu bars): the page ground, the
    # chrome's ink, the accent text on the active item, a divider line (theme_rules); the site
    # config names no background, so nothing overrides these
    rows += [("navbar-bg", v["bg"]), ("navbar-fg", v["titlebar_ink"]), ("navbar-hl", v["accent_text"]),
             ("footer-bg", v["bg"]), ("footer-fg", v["muted_solid"]),
             ("footer-border", "true"), ("footer-border-color", v["divider_solid"])]
    # Code on the system's panel vocabulary -- a surface in the page's ink (Bootstrap's own
    # defaults are black on near-white in every mode); syntax colours stay Quarto's (fedabcd0)
    rows += [("code-block-bg", v["surface"]), ("code-bg", v["surface"]), ("code-color", v["text"]),
             ("pre-color", v["text"])]
    rows += [(f"callout-color-{c}", v[role]) for c, role in CALLOUT_ROLES]
    rows += [
        ("font-family-sans-serif", _family(v["font_body"], g.get(v["font_body"]))),
        ("font-family-base", _family(v["font_body"], g.get(v["font_body"]))),
        ("headings-font-family", _family(v["font_heading"], g.get(v["font_heading"]))),
        ("headings-font-weight", v["heading_weight"]),
        ("font-weight-base", v["body_weight"]),
        ("font-size-root", _px(base)), ("font-size-base", "1rem"),
        ("line-height-base", v["line_height"]),
    ]
    if v["font_mono"]:
        rows.append(("font-family-monospace", _family(v["font_mono"], g.get(v["font_mono"], "monospace"))))
    for level in ("h1", "h2", "h3", "h4", "h5"):
        rows.append((f"{level}-font-size", _rem(v[f"fs_{level}"], base)))
    radius = tokens["radius"]
    for var, key in (("border-radius-sm", "sm"), ("border-radius", "md"), ("border-radius-lg", "lg")):
        if key in radius:
            rows.append((var, _px(radius[key])))
    # Bootstrap's spacer scale is [.25, .5, 1, 1.5, 3] x $spacer: four steps of the tokens'
    # base unit puts spacers 1..4 on the tokens' own steps 1, 2, 4 and 6
    if "4" in tokens["space"]:
        rows.append(("spacer", _px(tokens["space"]["4"])))
    return "\n".join(f"${k}: {val};" for k, val in rows) + "\n"


def theme_rules(tokens: Dict[str, Any]) -> str:
    """The rules the variables cannot carry: the per-level heading weights the type scale names
    (Bootstrap has one heading weight), the navbar's divider line (Quarto has a footer border
    variable and no navbar one), the code block's border on the divider (Quarto draws it in
    the block's own background), text selection as the system draws it -- the selection
    tint under the page's own ink, as the kit's text widgets do (Bootstrap sets none, so a
    browser's default showed) -- and the kit's roles on every other element a site renders
    (the audit of the kit's QSS against the site, amendment of 0858bbd0): scrollbars, menus
    and the search results, category tags, rules, focus, tables, tooltips -- and the kit's button
    and chip roles by name (`kit-button`, `kit-primary`, `kit-chip`) for a page that marks an
    element with the role it takes."""
    rules = [f"h{n}, .h{n} {{ font-weight: var(--fw-h{n}); }}" for n in range(1, 6) if f"h{n}" in tokens["type"]]
    rules += [".navbar { border-bottom: 1px solid var(--divider); }",
              "div.sourceCode { border-color: var(--divider); }",
              "::selection { background-color: var(--selection); color: var(--text); }"]
    # scrollbars: thin and quiet, a handle on no track (the kit's QScrollBar); the property inherits
    rules.append("html { scrollbar-width: thin; scrollbar-color: var(--scroll-handle) transparent; }")
    # menus: a surface with a divider edge, the highlighted item an accent tint in accent text (QMenu)
    rules.append(".dropdown-menu { --bs-dropdown-bg: var(--surface); --bs-dropdown-border-color: var(--divider); "
                 "--bs-dropdown-link-color: var(--text); --bs-dropdown-link-hover-bg: var(--accent-hover); "
                 "--bs-dropdown-link-hover-color: var(--accent-text); --bs-dropdown-link-active-bg: var(--accent-hover); "
                 "--bs-dropdown-link-active-color: var(--accent-text); }")
    # search results: the selected item as the kit's selected list item, a match as its find wash
    # (Quarto's own selectors, so the later rule wins at equal specificity)
    sel = [f"{root} li.aa-Item[aria-selected=true] .search-item" for root in (".aa-DetachedOverlay", "#quarto-search-results")]
    parts = (".search-result-more", " .search-result-section", " .search-result-text",
             " .search-result-title-container", " .search-result-text-container")
    rules.append(", ".join(sel) + " { background-color: var(--accent-hover); }")
    rules.append(", ".join(s + p for s in sel for p in parts)
                 + " { color: var(--accent-text); background-color: transparent; }")
    rules.append("mark, .mark, " + ", ".join(f"{s} mark.search-match, {s} .search-match.mark" for s in sel)
                 + " { color: inherit; background-color: var(--accent-press-tint); }")
    # categories: the kit's SECONDARY BUTTON -- every chip is an action (a listing's filters it, a
    # post's links into the category listing): ink on no fill, a divider edge, the hover / press
    # washes, an accent edge on keyboard focus (Quarto's own selectors: its post-page and listing
    # rules are more specific than a bare class)
    chips = (".quarto-title .quarto-categories .quarto-category", "div.quarto-post .listing-categories .listing-category",
             ".quarto-grid-item .listing-categories .listing-category")
    rules.append(", ".join(chips) + " { color: var(--text); background-color: transparent; border: 1px solid "
                 "var(--divider); border-radius: var(--radius-md); opacity: 1; text-decoration: none; cursor: pointer; }")
    rules.append(", ".join(c + ":hover" for c in chips) + " { background-color: var(--text-hover); color: var(--text); }")
    rules.append(", ".join(c + ":active" for c in chips) + " { background-color: var(--text-pressed); }")
    rules.append(", ".join(c + ":focus-visible" for c in chips) + " { border-color: var(--accent); outline: none; }")
    # the kit's roles by name, for an element a page marks with the role it takes (design 8b4f15d0
    # (8) / (7)): `kit-button` is the SECONDARY BUTTON (QPushButton), `kit-primary` its primary
    # variant (accent ink and edge), `kit-chip` the category chip above at a page's own size
    rules.append(".kit-button, .kit-chip { display: inline-block; color: var(--text); background-color: transparent; "
                 "border: 1px solid var(--divider); border-radius: var(--radius-md); text-decoration: none; "
                 "cursor: pointer; }")
    rules.append(".kit-button { font-family: var(--font-heading); font-weight: var(--heading-weight); "
                 "padding: var(--space-1) var(--space-4); }")
    rules.append(".kit-chip { font-size: 0.8em; padding: 0 var(--space-2); }")
    rules.append(".kit-button:hover, .kit-chip:hover { background-color: var(--text-hover); color: var(--text); }")
    rules.append(".kit-button:active, .kit-chip:active { background-color: var(--text-pressed); }")
    rules.append(".kit-button:focus-visible, .kit-chip:focus-visible { border-color: var(--accent); outline: none; }")
    rules.append(".kit-button.kit-primary { color: var(--accent-text); border-color: var(--accent); }")
    rules.append(".kit-button.kit-primary:hover { background-color: var(--accent-hover); color: var(--accent-text); }")
    rules.append(".kit-button.kit-primary:active { background-color: var(--accent-press-tint); "
                 "border-color: var(--accent-pressed); }")
    rules.append(".kit-button.kit-primary:focus-visible { box-shadow: 0 0 0 1px var(--accent); }")
    # a finger needs a bigger target than a pointer (the review of b5385504: chips pressed wrong on
    # a phone and a tablet): under a coarse pointer every chip grows to a 2rem touch target, the
    # fine-pointer size unchanged
    rules.append("@media (pointer: coarse) { " + ", ".join(chips + (".kit-chip",))
                 + " { display: inline-flex; align-items: center; min-height: 2rem; "
                 "padding: 0 var(--space-3); margin: 0 var(--space-1) var(--space-1) 0; } }")
    # rules: the divider
    rules.append("hr { color: var(--divider); opacity: 1; }")
    # focus: an accent edge, no glow (the kit's :focus)
    rules.append(".form-control:focus, .form-select:focus { border-color: var(--accent); box-shadow: none; }")
    rules.append(".aa-Autocomplete .aa-Form:focus-within, .aa-DetachedFormContainer .aa-Form:focus-within "
                 "{ box-shadow: 0 0 0 1px var(--accent); }")
    # tables: hairline rows on the divider, the alternate and hover rows, a quieter header (QAbstractItemView)
    rules.append(".table { --bs-table-border-color: var(--divider); --bs-table-striped-bg: var(--row-alt); "
                 "--bs-table-hover-bg: var(--row-hover); --bs-table-active-bg: var(--accent-hover); }")
    rules.append(".table > thead th, .table > thead td { color: var(--header-text); }")
    # tooltips: a surface in the page's ink with a divider edge (QToolTip)
    rules.append(".tooltip { --bs-tooltip-bg: var(--surface); --bs-tooltip-color: var(--text); }")
    rules.append(".tooltip-inner { border: 1px solid var(--divider); }")
    return "\n".join(rules) + "\n"


def theme_scss(
    tokens: Dict[str, Any],     # A checked schema-v1 system
    mode: str,                  # The mode this file renders
    faces_css: str = "",        # The @font-face rules (`web_fonts(...)["css"]`)
    generics: Optional[Dict[str, str]] = None,  # {family: generic} (`web_fonts(...)["generics"]`)
) -> str:  # A Quarto theme file (scss:defaults + scss:rules)
    """One Quarto theme file for one mode of a system."""
    head = "// %s (%s) -- projected by cjm-design-system from the system's tokens; never edit\n" % (
        tokens["name"], mode)
    return (head + "/*-- scss:defaults --*/\n" + bootstrap_defaults(tokens, mode, generics)
            + "\n/*-- scss:rules --*/\n" + (faces_css + "\n" if faces_css else "")
            + T.to_css(tokens, mode=mode) + "\n" + theme_rules(tokens))


# ---- fonts ----------------------------------------------------------------------

def font_files(
    tokens: Dict[str, Any],     # A system's tokens
    system_dir: Path,           # The directory its tokens.json sits in
) -> List[Path]:  # The font files its `fonts.files` globs name under <system_dir>/fonts, sorted
    """The files a system's tokens name, resolved the way the Qt kit registers them."""
    fonts_dir = Path(system_dir) / "fonts"
    out: List[Path] = []
    for pat in tokens["fonts"].get("files") or ["*.ttf", "*.otf"]:
        out += [p for p in sorted(fonts_dir.glob(pat)) if p not in out]
    return out


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _describe(font: Any) -> Dict[str, Any]:
    """Family, style, weight range and generic family, read from the font itself."""
    names = font["name"]
    family = str(names.getDebugName(16) or names.getDebugName(1) or "")
    os2 = font["OS/2"] if "OS/2" in font else None
    italic = bool((os2 and os2.fsSelection & 1) or font["head"].macStyle & 2
                  or ("post" in font and font["post"].italicAngle != 0))
    weight: Tuple[int, int]
    axes = {a.axisTag: a for a in font["fvar"].axes} if "fvar" in font else {}
    if "wght" in axes:
        weight = (int(axes["wght"].minValue), int(axes["wght"].maxValue))
    else:
        w = int(os2.usWeightClass) if os2 else 400
        weight = (w, w)
    # The generic fallback only where the file DECLARES one (PANOSE): many fonts leave the
    # classification at 0, and then no generic is guessed
    generic = None
    if os2 is not None:
        p = os2.panose
        if p.bProportion == 9:
            generic = "monospace"
        elif p.bFamilyType == 2:   # Latin text: serif style 11..13 = sans, 2..10 = serif
            generic = "sans-serif" if p.bSerifStyle in (11, 12, 13) else ("serif" if 2 <= p.bSerifStyle <= 10 else None)
        elif p.bFamilyType == 3:
            generic = "cursive"
    return {"family": family, "style": "italic" if italic else "normal", "weight": weight, "generic": generic}


def web_fonts(
    files: List[Path],          # The system's font files (`font_files`)
    out_dir: Path,              # Where the woff2 files are written (emptied of anything this call did not write)
    url_prefix: str,            # The prefix the @font-face src urls carry ("fonts/classical/")
    families: Optional[Iterable[str]] = None,  # The families the tokens name (a file outside them is reported)
) -> Dict[str, Any]:  # {css, files, faces, sources, generics, unmatched, converted, reused}
    """Convert each font file into woff2 subsets by unicode range and return the @font-face
    rules naming them. Output is deterministic (no timestamp is recalculated) and a subset
    whose source hash and range are unchanged since the last call is reused, not rebuilt --
    a theme rebuild costs what changed (ruling ee35f222)."""
    from fontTools import subset
    from fontTools import version as ft_version
    from fontTools.ttLib import TTFont

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / _MANIFEST
    try:
        old = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        old = {}
    tool = f"fonttools {ft_version}"
    latin, latin_ext = parse_ranges(LATIN_RANGES), parse_ranges(LATIN_EXT_RANGES)
    wanted = set(families) if families is not None else None
    manifest: Dict[str, Any] = {}
    faces: List[Dict[str, Any]] = []
    sources: List[Dict[str, Any]] = []
    unmatched: List[str] = []
    written: List[Dict[str, Any]] = []
    converted = reused = 0
    for src in files:
        digest = sha256_file(src)
        sources.append({"path": str(src), "sha256": digest})
        font = TTFont(str(src), recalcTimestamp=False)
        desc = _describe(font)
        if wanted is not None and desc["family"] not in wanted:
            unmatched.append(f"{src.name}: family {desc['family']!r} is not one the tokens name")
            continue
        cmap = set(font.getBestCmap() or {})
        ranges = [("latin", cmap & latin, LATIN_RANGES), ("latin-ext", cmap & latin_ext, LATIN_EXT_RANGES)]
        rest = cmap - latin - latin_ext
        ranges.append(("rest", rest, format_ranges(rest) if rest else ""))
        stem = f"{_slug(desc['family'])}-{desc['style']}"
        face = {**desc, "source": src.name, "subsets": []}
        for name, points, spec in ranges:
            if not points:
                continue
            fname = f"{stem}-{name}.woff2"
            dest = out_dir / fname
            key = {"source_sha256": digest, "range": spec, "tool": tool}
            if old.get(fname) == key and dest.is_file():
                reused += 1
            else:
                part = TTFont(str(src), recalcTimestamp=False)
                opts = subset.Options()
                opts.flavor = "woff2"
                opts.layout_features = ["*"]
                opts.name_IDs = ["*"]
                opts.name_languages = ["*"]
                opts.notdef_outline = True
                opts.recalc_timestamp = False
                sub = subset.Subsetter(opts)
                sub.populate(unicodes=sorted(points))
                sub.subset(part)
                part.flavor = "woff2"
                part.save(str(dest))
                converted += 1
            manifest[fname] = key
            written.append({"file": fname, "bytes": dest.stat().st_size, "sha256": sha256_file(dest)})
            face["subsets"].append({"file": fname, "unicode_range": spec})
        faces.append(face)
    for stale in out_dir.iterdir():
        if stale.name != _MANIFEST and stale.name not in manifest:
            stale.unlink()
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    css: List[str] = []
    for f in faces:
        lo, hi = f["weight"]
        for s in f["subsets"]:
            css.append("@font-face {\n  font-family: \"%s\";\n  font-style: %s;\n  font-weight: %s;\n"
                       "  font-display: swap;\n  src: url(\"%s%s\") format(\"woff2\");\n  unicode-range: %s;\n}"
                       % (f["family"], f["style"], lo if lo == hi else f"{lo} {hi}", url_prefix, s["file"],
                          s["unicode_range"]))
    generics = {f["family"]: f["generic"] for f in faces if f["generic"]}
    return {"css": "\n".join(css), "files": written, "faces": faces, "sources": sources,
            "generics": generics, "unmatched": unmatched, "converted": converted, "reused": reused}

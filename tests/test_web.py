"""The web projections (design 0858bbd0 (3) + (4)): a per-mode variable layer in
the CSS form a browser reads, one Quarto theme file per mode whose every value
comes from the tokens, and the fonts as woff2 subsets by unicode range that lose
no glyph, read their weight range from the font, and rebuild only what changed."""

import re

import pytest

from cjm_design_system import systems, web
from cjm_design_system import tokens as T


@pytest.fixture(params=["classical", "netrunner"])
def seed(request):
    return request.param, T.load(systems.tokens_path(request.param))


def test_to_css_one_mode_lands_on_the_selector_alone(seed):
    slug, tok = seed
    for mode in T.modes(tok):
        css = T.to_css(tok, mode=mode)
        assert "[data-mode=" not in css
        assert css.count(":root {") == 1
        assert f"--bg: {T.resolve(tok, mode)['bg']};" in css
        assert "--neutral-900:" in css and "--fs-h1:" in css   # the static layer rides every mode
    with pytest.raises(KeyError):
        T.to_css(tok, mode="no-such-mode")


def test_to_css_writes_tints_in_the_css_form(seed):
    """resolve's QSS rgba carries a 0-255 alpha a browser would clamp to opaque."""
    slug, tok = seed
    for css in [T.to_css(tok)] + [T.to_css(tok, mode=m) for m in T.modes(tok)]:
        alphas = [float(a) for a in re.findall(r"rgba\(\d+, \d+, \d+, ([\d.]+)\)", css)]
        assert alphas and all(0 <= a <= 1 for a in alphas)


def test_theme_scss_values_come_from_the_tokens(seed):
    slug, tok = seed
    for mode in T.modes(tok):
        scss = web.theme_scss(tok, mode)
        defaults, rules = scss.split("/*-- scss:rules --*/")
        assert "/*-- scss:defaults --*/" in defaults
        v = T.resolve(tok, mode)
        known = {str(x).lower() for x in v.values()} | {c.lower() for r in tok["ramps"].values() for c in r}
        for hexv in re.findall(r"#[0-9a-fA-F]{6}", defaults):
            assert hexv.lower() in known, hexv
        assert f"$body-bg: {v['bg']};" in defaults and f"$primary: {v['accent']};" in defaults
        assert f'$headings-font-family: "{v["font_heading"]}"' in defaults
        assert "[data-mode=" not in rules and "googleapis" not in scss


def test_empty_mono_slot_leaves_bootstraps_stack(seed):
    slug, tok = seed
    defaults = web.bootstrap_defaults(tok, T.modes(tok)[0])
    assert ("$font-family-monospace" in defaults) == bool(tok["fonts"].get("mono", {}).get("family"))


def test_chrome_greys_and_code_follow_the_system_in_every_mode(seed):
    """The navbar / footer on the page ground in the chrome's ink, code on a surface in the
    page's ink, and Bootstrap's greys on the neutral ramp -- step 100 nearest the page in
    either mode (the ramp reversed where the page is darker than its ink)."""
    slug, tok = seed
    neutral = tok["ramps"]["neutral"]
    for mode in T.modes(tok):
        v = T.resolve(tok, mode)
        d = web.bootstrap_defaults(tok, mode)
        assert f"$navbar-bg: {v['bg']};" in d and f"$navbar-fg: {v['titlebar_ink']};" in d
        assert f"$footer-bg: {v['bg']};" in d and "$footer-border: true;" in d
        assert f"$code-block-bg: {v['surface']};" in d and f"$pre-color: {v['text']};" in d
        dark = sum(T._rgb(v["bg"])) < sum(T._rgb(v["text"]))
        assert f"$gray-100: {neutral[8] if dark else neutral[0]};" in d
        assert f"$gray-900: {neutral[0] if dark else neutral[8]};" in d
    rules = web.theme_rules(tok)
    assert ".navbar { border-bottom: 1px solid var(--divider); }" in rules
    assert "::selection { background-color: var(--selection); color: var(--text); }" in rules
    # every variable a rule reads is one the mode's block defines (the whole vocabulary rides to_css)
    for mode in T.modes(tok):
        css = T.to_css(tok, mode=mode)
        for name in set(re.findall(r"var\(--([a-z0-9-]+)\)", rules)):
            assert f"--{name}:" in css, (mode, name)
    for mode in T.modes(tok):   # the variables the selection reads ride every mode's block
        css = T.to_css(tok, mode=mode)
        assert "--selection: rgba(" in css and f"--text: {T.resolve(tok, mode)['text']};" in css


def test_ranges_round_trip():
    pts = web.parse_ranges("U+0041-0043, U+0100, U+0102-0103")
    assert pts == {0x41, 0x42, 0x43, 0x100, 0x102, 0x103}
    assert web.parse_ranges(web.format_ranges(pts)) == pts
    assert web.format_ranges([0x41, 0x42, 0x44]) == "U+0041-0042, U+0044"


def _cmap(path):
    from fontTools.ttLib import TTFont
    return set(TTFont(str(path)).getBestCmap() or {})


def test_web_fonts_lose_no_glyph_and_read_the_weight_axis(tmp_path):
    pytest.importorskip("fontTools")
    tok = T.load(systems.tokens_path("classical"))
    files = [p for p in web.font_files(tok, systems.locate("classical")) if p.name.startswith("Lora[")]
    assert files
    r = web.web_fonts(files, tmp_path / "out", "fonts/classical/", families={"Lora"})
    assert r["unmatched"] == [] and r["converted"] == len(r["files"])
    (face,) = r["faces"]
    assert face["family"] == "Lora" and face["style"] == "normal" and face["weight"] == (400, 700)
    covered = set().union(*(_cmap(tmp_path / "out" / s["file"]) for s in face["subsets"]))
    assert covered >= _cmap(files[0])   # every code point the TTF maps is in some subset
    assert 'font-weight: 400 700;' in r["css"] and 'url("fonts/classical/lora-normal-latin.woff2")' in r["css"]
    assert sum(f["bytes"] for f in r["files"]) < files[0].stat().st_size


def test_web_fonts_reuse_unchanged_subsets_and_prune_stale_files(tmp_path):
    pytest.importorskip("fontTools")
    tok = T.load(systems.tokens_path("classical"))
    files = [p for p in web.font_files(tok, systems.locate("classical")) if p.name.startswith("Lora[")]
    out = tmp_path / "out"
    first = web.web_fonts(files, out, "f/")
    (out / "stale.woff2").write_bytes(b"x")
    again = web.web_fonts(files, out, "f/")
    assert again["converted"] == 0 and again["reused"] == len(first["files"])
    assert not (out / "stale.woff2").exists()
    assert [f["sha256"] for f in again["files"]] == [f["sha256"] for f in first["files"]]
    fresh = web.web_fonts(files, tmp_path / "fresh", "f/")   # deterministic: no timestamp recalculated
    assert [f["sha256"] for f in fresh["files"]] == [f["sha256"] for f in first["files"]]


def test_web_fonts_report_a_family_the_tokens_do_not_name(tmp_path):
    pytest.importorskip("fontTools")
    tok = T.load(systems.tokens_path("classical"))
    files = [p for p in web.font_files(tok, systems.locate("classical")) if p.name.startswith("Lora[")]
    r = web.web_fonts(files, tmp_path / "out", "f/", families={"Cormorant Garamond"})
    assert r["faces"] == [] and len(r["unmatched"]) == 1 and "Lora" in r["unmatched"][0]


def test_static_fonts_take_the_os2_weight():
    pytest.importorskip("fontTools")
    from fontTools.ttLib import TTFont
    tok = T.load(systems.tokens_path("netrunner"))
    by_name = {p.name: p for p in web.font_files(tok, systems.locate("netrunner"))}
    bold = web._describe(TTFont(str(by_name["CourierPrime-Bold.ttf"])))
    assert bold["weight"] == (700, 700) and bold["generic"] == "monospace"
    assert web._describe(TTFont(str(by_name["CourierPrime-Italic.ttf"])))["style"] == "italic"

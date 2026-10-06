# Changelog

The library's release record. Each entry names the ruling or work item the
change served, so a version reads back to its decision on the graph.

## 0.0.2 — unreleased

The web projections of a Quarto site's theme (leg C of design 0858bbd0, build
4bd47051; amendments 4b58c9db, 898c81d6, 6566f33a, 6af37fc3).

- `web` (new; the `web` extra adds fontTools and brotli) — one Quarto theme
  file per mode: Bootstrap's variables as literal values from `resolve`
  (the page and state colours, Quarto's callouts, the chrome, code on the
  surface, the grey scale on the neutral ramp, reversed in a dark mode, the
  fonts and the type scale), and the rules the variables cannot carry (heading
  weights, the navbar's divider, text selection, scrollbars, menus and search
  results, category chips as the kit's secondary button, rules, focus, tables,
  tooltips); the fonts as woff2 subsets by unicode range, weight ranges read
  from each font, deterministic, an unchanged subset reused.
- `web.theme_rules` — the kit's roles by name for a page that marks an element
  with the role it takes: `kit-button` (the secondary button), `kit-primary`
  (accent ink and edge), `kit-chip` (the category chip); under a coarse
  pointer every chip role grows to a 2rem touch target (the home page's build
  bf2ea1b9, design 8b4f15d0, amendment 2cabfd2f).
- `tokens.to_css` — `mode=` emits one mode's block on the selector (Quarto
  swaps whole stylesheets); every colour of the resolved vocabulary is
  emitted, not a subset; tints are written in the CSS form — the QSS rgba's
  0–255 alpha read as opaque in a browser.

## 0.0.1 — 2026-10-02

Born from cjm-substrate-qt-kit (design 0858bbd0, the theme half of the
redesign build 8079ae0f): the design system's data and its headless half
move out of the Qt kit so a web build never needs PySide6.

- `tokens` — token schema v1 as the kit shipped it in 0.0.8 (check, resolve,
  to_css, the colour helpers); `to_css` now names this library in its header.
- `systems` — the vendored seed systems' data: Classical and Netrunner, each
  its tokens.json and its OFL fonts; `available` / `locate` / `tokens_path`.
  Each system's QSS templates and painted widgets stay in the kit.
- `tools.css_to_tokens` — the importer for a web-first system's CSS.

# Changelog

The library's release record. Each entry names the ruling or work item the
change served, so a version reads back to its decision on the graph.

## 0.0.1 — unreleased

Born from cjm-substrate-qt-kit (design 0858bbd0, the theme half of the
redesign build 8079ae0f): the design system's data and its headless half
move out of the Qt kit so a web build never needs PySide6.

- `tokens` — token schema v1 as the kit shipped it in 0.0.8 (check, resolve,
  to_css, the colour helpers); `to_css` now names this library in its header.
- `systems` — the vendored seed systems' data: Classical and Netrunner, each
  its tokens.json and its OFL fonts; `available` / `locate` / `tokens_path`.
  Each system's QSS templates and painted widgets stay in the kit.
- `tools.css_to_tokens` — the importer for a web-first system's CSS.

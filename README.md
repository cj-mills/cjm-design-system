# cjm-design-system

<!-- generated from the context graph by `cjm-context-graph readme` — do not edit by hand; edit the graph (the urge to hand-edit = move it on-graph) -->

A design system as data (ruling a439c226): token schema v1 with its check and its headless resolution into one flat vocabulary, the CSS custom-properties projection for the web, the vendored seed systems Classical and Netrunner with their OFL fonts, and the importer for a web-first system's CSS. Nothing here imports Qt, so a web build never needs PySide6; the Qt kit (cjm-substrate-qt-kit) consumes the same tokens and keeps only what Qt reads. Born out of the kit by design 0858bbd0, the theme half of the public-site redesign build 8079ae0f.

## Modules

- **`cjm_design_system.__init__`** — A design system as DATA (ruling a439c226): one canonical tokens file per
- **`cjm_design_system.systems.__init__`** — The design systems this library ships as DATA (ruling a439c226): one
- **`cjm_design_system.tokens`** — Token schema v1 — a design system as DATA, resolved headlessly (ruling
- **`cjm_design_system.tools.__init__`** — Design-system tools (run as modules):
- **`cjm_design_system.tools.build`** — Build the static web projections of a design system: the CSS
- **`cjm_design_system.tools.css_to_tokens`** — Import a web-first design system's CSS into a schema-v1 tokens file.

## API

### `cjm_design_system.systems.__init__`

- `available` _function_ — Every vendored system slug (a directory carrying a tokens.json).
- `locate` _function_ — The directory of a system: a vendored slug, a directory holding a
- `tokens_path` _function_

### `cjm_design_system.tokens`

- `SchemaError` _class_ — A tokens file that violates schema v1 — every problem listed, so one
- `check` _function_ — Refuse a malformed system loudly: every missing / mistyped field named
- `load` _function_ — Read a tokens file (JSON). `check` it before resolving anything.
- `mix` _function_ — Flatten `fg` at opacity `t` over `bg` -> a solid hex (QPalette, painters,
- `mode_for_scheme` _function_ — The mode the system maps an OS scheme ("light" / "dark") onto — None
- `modes` _function_
- `resolve` _function_ — tokens + mode -> the flat vocabulary every projection reads: the QSS
- `rgba` _function_ — QSS rgba() with a 0-255 alpha (the form every Qt 6 version parses).
- `slug` _function_ — The system's file-system / preference slug: lower-case, spaces -> dashes.
- `to_css` _function_ — The CSS custom-properties layer for a system — the ruling's second
- `to_hex` _function_

### `cjm_design_system.tools.build`

- `main` _function_

### `cjm_design_system.tools.css_to_tokens`

- `convert` _function_
- `darker` _function_
- `family` _function_
- `main` _function_
- `parse_root` _function_
- `px` _function_
- `ramp` _function_

## Dependencies

**Used by:** `cjm-context-graph-projection`, `cjm-substrate-qt-kit`

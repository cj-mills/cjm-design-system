# cjm-design-system

<!-- generated from the context graph by `cjm-context-graph readme` — do not edit by hand; edit the graph (the urge to hand-edit = move it on-graph) -->

_No purpose recorded on-graph yet — author it with_ `assert 1268773e-7e8b-5609-9c2d-e2f6ffeee290 purpose "…"` _(or by the repo's entity key)._

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

**Used by:** `cjm-substrate-qt-kit`

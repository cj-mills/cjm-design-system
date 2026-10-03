"""A design system as DATA (ruling a439c226): one canonical tokens file per
system, from which every consumer derives what it renders — the web (the CSS
custom-properties layer for the Quarto sites, 8079ae0f) and the Qt kit
(cjm-substrate-qt-kit: QPalette + QSS + fonts + icons) alike.

This library holds the half no consumer class owns (design 0858bbd0): token
schema v1 with its check and its headless resolution into one flat vocabulary
(`tokens`), the vendored seed systems' data — each system's tokens.json and
the font files it names (`systems`: Classical and Netrunner) — and the
importer for a web-first system's CSS (`tools.css_to_tokens`). Nothing here
imports Qt, so a web build never needs PySide6; what only Qt reads (QSS
templates, painted widgets, the Theme runtime) stays in the kit.
"""

__version__ = "0.0.2"

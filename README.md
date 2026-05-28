# Codex Web Page Parity

Shareable Codex plugin for pixel-parity and screenshot-to-page matching workflows.

This repository packages the `web-page-parity` skill as a reusable plugin and exposes it through a repo-local marketplace so other Codex users can install it from GitHub.

## What It Includes

- A `web-page-parity` skill for matching live pages to PNG, PDF, Figma exports, and browser comments.
- Bundled Python scripts for deterministic page capture, side-by-side reports, OCR box comparison, and stateful screenshot capture.
- A repo marketplace entry so the plugin can be discovered from this repository.

## Install From GitHub

Add this repository as a marketplace source:

```bash
codex plugin marketplace add 8866Jason/codex-web-page-parity
```

Then restart Codex, open the plugin directory, select the `Web Page Parity Plugins` marketplace, and install `Web Page Parity`.

## Local Layout

```text
.
├── .agents/plugins/marketplace.json
└── plugins/web-page-parity/
    ├── .codex-plugin/plugin.json
    └── skills/web-page-parity/
```

## Runtime Requirements

The bundled scripts assume a machine with:

- Python 3
- Chrome or Chromium
- Playwright available to the local environment
- Pillow installed for image processing

Some workflows may optionally use `tesseract` for OCR-based typography checks.

## Privacy Defaults

- Capture scripts do not collect browser console logs by default.
- Capture scripts do not record sampled page text by default.
- Opt in only when needed with `--include-console-logs` or `--include-text-content`.

## Development Notes

- The skill itself lives at `plugins/web-page-parity/skills/web-page-parity`.
- The plugin manifest lives at `plugins/web-page-parity/.codex-plugin/plugin.json`.
- The marketplace entry lives at `.agents/plugins/marketplace.json`.

## Versioning

Current sanitized packaging version: `0.1.1`.

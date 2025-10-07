# mem8 Agent Development Guide

This guide sets expectations for contributors and local development when working with mem8. It prioritizes uv for environment management and tool execution across Windows, macOS, and Linux.

## Dev Environment (uv)

- Use uv for everything: creation, execution, and tool installation.
- Initial setup (installs dev extras): `uv sync --extra dev`
- Run commands via uv: `uv run <cmd>` (e.g., `uv run pytest`, `uv run mem8 --help`).

## Global Tool in Editable Mode

To use the mem8 CLI while you’re working in other folders on this dev box, install it as a global uv tool in editable mode:

- Install (once): `uv tool install . --editable`
- This creates a global `mem8` entry point that references your local checkout so code changes are picked up immediately.
- Ensure the uv tool bin directory is on your PATH. If `mem8` is not found after install, re-open your shell or add uv’s tool bin to PATH (uv prints this path during install).

Common workflows:
- Run CLI anywhere: `mem8 status` (or `uv tool run mem8 status`)
- Upgrade/reinstall after major changes: `uv tool install . --editable`
- Remove if needed: `uv tool uninstall mem8`

## Testing & Linting

- Run all tests: `uv run pytest`
- Subset by marker: `uv run pytest -m unit`
- Lint/format (root): `make lint`, `make format`

## Notes

- Windows symlink behavior: mem8 falls back to directories if symlinks/junctions aren’t permitted.
- Network optional: tests and CLI functions avoid network calls; GitHub CLI is used only when present.
- Never commit secrets. Use provided `.env.*.example` templates.


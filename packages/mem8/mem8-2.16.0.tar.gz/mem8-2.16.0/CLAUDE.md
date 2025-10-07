- Use conventional commits as this project uses github actions that auto-publish .github\workflows\release.yml
- there's already a copy setup with @DOCKER.md that should be hot reloading and browsable to test

## Development Workflow with uv

**CRITICAL**: Always use `uv` for all Python operations in this project. Never use `pip`, `python`, or `pytest` directly.

### CLI Development (Most Common)

When working on the mem8 CLI, always ensure it's installed in **editable mode**:

```bash
# 1. Verify/install editable mode (do this at start of every session)
uv tool install . --editable

# 2. Now test CLI commands as users will experience them
mem8 --help
mem8 status
mem8 search "query"

# 3. After making changes to cli_typer.py, re-install to pick up changes
uv tool install . --editable
```

**Why editable mode?**
- Commands execute as `mem8` (not `uv run mem8`)
- Reflects actual user experience
- Tests the installed command structure
- Automatically picks up code changes after reinstall

### Other uv Commands

```bash
# Install/update dependencies
uv sync                              # Sync all dependencies from pyproject.toml

# Add new dependencies
uv add requests                      # Add runtime dependency
uv add --dev pytest                  # Add dev dependency
uv add --optional server fastapi     # Add to [project.optional-dependencies]

# Run scripts/tests (use when NOT testing CLI directly)
uv run pytest                        # Run tests
uv run python scripts/test-ui.py     # Run scripts
uv run mypy mem8                     # Run type checking

# DO NOT USE: pip, python -m, or bare pytest commands
```

### Quick Reference

| Task | Command | Why |
|------|---------|-----|
| CLI development | `uv tool install . --editable` | Install as real command |
| Test CLI | `mem8 <command>` | Test as users experience it |
| Run tests | `uv run pytest` | Run with proper environment |
| Add dependency | `uv add package` | Manages pyproject.toml |
| Sync deps | `uv sync` | Updates from pyproject.toml |
| Run scripts | `uv run python script.py` | Uses project environment |

### Verification Checklist

Before testing CLI changes:
1. ✅ Run `uv tool install . --editable`
2. ✅ Verify with `mem8 --version`
3. ✅ Test command: `mem8 <your-command>`
4. ✅ Check output matches expected user experience

## Template Management

- The `.claude` directory in this repo is generated from `mem8\templates\claude-dot-md-template`
- When updating commands or agents, **always modify the cookiecutter template** in `mem8\templates\claude-dot-md-template\{{cookiecutter.project_slug}}\`
- Changes to the template will be applied to new projects when users run `mem8 init`
- The local `.claude` directory is just for testing the mem8 CLI itself - it will be regenerated from templates
- Same applies to the `thoughts` directory structure which comes from `mem8\templates\shared-thoughts-template`
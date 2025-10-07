# mem8 - Claude Code Workspace Manager

A streamlined CLI tool for managing Claude Code customizations and documentation workflows. Create standardized project templates, manage memory/research documents, and enhance your Claude Code development experience.

## 🎯 Overview

mem8 is designed to work seamlessly with Claude Code, providing:
- **💻 Rich CLI Interface** - Manage Claude Code customizations and project templates  
- **📝 Memory Management** - Organize research, plans, and documentation in markdown
- **🎨 Dashboard** - Optional web interface to browse your workspace and memory
- **🏗️ Template System** - Cookiecutter templates for Claude Code configurations

## ✨ Core Features

### 💻 CLI Commands
```bash
mem8 init --template claude-config   # Initialize Claude Code workspace
mem8 status                          # Check workspace health
mem8 doctor                          # Diagnose issues and check CLI toolbelt
mem8 doctor --fix                    # Auto-fix missing tools (where possible)
mem8 doctor --json                   # Machine-readable output for agents
mem8 tools                           # List toolbelt CLI tools and versions
mem8 tools --save                    # Save toolbelt to .mem8/tools.md
mem8 ports --lease                   # Lease port range for project
mem8 ports                           # Show current project's port assignments
mem8 ports --kill <port>             # Kill process on port (safe mode)
mem8 search "query"                  # Search across all memory
mem8 serve                           # Start the API server (port 8000)
```

### 📁 Template System
- **claude-dot-md-template** - Generate `.claude/[agents,commands]` configurations
- **shared-memory-template** - Create structured memory repositories
- **Cookiecutter integration** - Flexible, customizable project generation

### 🔍 Memory Organization
```
memory/
├── shared/
│   ├── research/      # Research documents
│   ├── plans/         # Implementation plans  
│   ├── prs/          # PR descriptions
│   └── decisions/     # Technical decisions
└── {project}/         # Project-specific memory
```

## 🚀 Quick Start

### 1. Install mem8
```bash
# Install with uv (recommended)
uv tool install mem8

# Or install from source
git clone https://github.com/killerapp/mem8.git
cd mem8
uv tool install --editable .
```

### 2. Initialize Your Workspace
```bash
# Create Claude Code configuration
mem8 init --template claude-config

# Create memory repository
mem8 init --template memory-repo

# Check everything is working
mem8 status
```

### 3. Optional: Start the Web Interface

**For CLI-only usage, skip this step.** The web interface is optional and provides a browser-based viewer.

```bash
# Option A: Frontend only (simple file viewer)
cd frontend && npm install && npm run dev
# Access at http://localhost:22211

# Option B: Full stack with backend (for teams/auth features)
docker-compose --env-file .env.dev up -d
# Frontend at http://localhost:22211
# Backend API at http://localhost:8000
# API Docs at http://localhost:8000/docs

# Option C: Hybrid (backend in Docker, frontend native)
docker-compose --env-file .env.dev up -d backend db
cd frontend && npm install && npm run dev
# Best for frontend development
```

**Note:** The `mem8 serve` command requires Docker for the database. See [DOCKER.md](DOCKER.md) for details.

## 🔧 CLI Toolbelt Management

mem8 includes a CLI toolbelt verification system to ensure you have all necessary tools for AI-assisted development workflows.

### Quick Check
```bash
# Check for missing tools
mem8 doctor

# Auto-install missing tools (where supported)
mem8 doctor --fix

# JSON output for agents/CI
mem8 doctor --json
```

### Verified Tools

The toolbelt checks for essential CLI tools that enhance AI workflows:

**Required Tools:**
- **ripgrep** (`rg`) - Fast recursive search, better than grep
- **fd** (`fd`) - Fast file finder, better than find
- **jq** - JSON processor for parsing API responses
- **gh** - GitHub CLI for PR/issue management
- **git** - Version control system

**Optional Tools:**
- **bat** - Syntax-highlighted file viewer
- **delta** - Beautiful git diff viewer
- **yq** - YAML/XML processor
- **fzf** - Fuzzy finder for interactive selection
- **sd** - Simpler sed alternative for text replacement
- **ast-grep** - AST-based code search and refactoring

### Version Requirements

Tools with version requirements are automatically checked:
```bash
$ mem8 doctor
⚠️  Missing 1 required CLI tools
  • gh (gh) (requires >=2.60) - GitHub CLI
    Install: winget install GitHub.cli
    Current: 2.53.0
```

### Platform Support

Install commands are automatically selected for your platform:
- **Windows** - Uses `winget` package manager
- **macOS** - Uses `brew` (Homebrew)
- **Linux** - Uses `apt` or distro-specific managers

### CI Integration

The `--json` flag and exit codes make it CI-friendly:
```bash
mem8 doctor --json > toolbelt-status.json
# Exit code 0 if all tools present, 1 if any missing
```

### External Template Sources

Doctor can use custom toolbelt definitions from external template sources:

**Priority Order:**
1. CLI flag: `--template-source`
2. Project config: `.mem8/config.yaml`
3. User config: `~/.config/mem8/config.yaml`
4. Builtin templates (default)

**Project-Level Configuration** (`.mem8/config.yaml`):
```yaml
templates:
  # Dedicated template repo (root-level)
  default_source: "my-org/templates"

  # Fork of killerapp/mem8-templates
  default_source: "acme-corp/mem8-templates"

  # Monorepo with templates in subdirectory
  default_source: "my-org/monorepo#subdir=mem8/templates"

  # Specific version/tag
  default_source: "my-org/templates@v1.0.0"

  # Local development path
  default_source: "/path/to/templates"
```

**User-Level Configuration** (`~/.config/mem8/config.yaml`):
```bash
# Set default for all projects
mem8 templates set-default "org/repo"

# Or edit manually at ~/.config/mem8/config.yaml
```

**CLI Override:**
```bash
# Dedicated template repo (cleanest for organizations)
mem8 doctor --template-source "acme-corp/mem8-templates"

# Fork of official templates with customizations
mem8 doctor --template-source "my-org/mem8-templates"

# Monorepo with templates in subdirectory
mem8 doctor --template-source "my-org/monorepo#subdir=tools/templates"

# Use specific version/branch
mem8 doctor --template-source "my-org/templates@v2.0.0"

# Local development version
mem8 doctor --template-source "/path/to/local/templates"
```

**Template Repo Patterns:**

1. **Dedicated Repo (Recommended for Organizations)**
   - Fork `killerapp/mem8-templates` → `acme-corp/mem8-templates`
   - Customize toolbelt for your org's standards
   - Reference directly: `acme-corp/mem8-templates`
   - No `#subdir=` needed - manifest at root

2. **Monorepo with Templates**
   - Keep templates alongside code
   - Use `#subdir=path/to/templates`
   - Example: `my-org/platform#subdir=config/mem8-templates`

3. **Local Development**
   - Test changes before pushing
   - Use absolute or relative paths
   - Example: `--template-source ./my-templates`

### Custom Toolbelts

Projects can define custom tool requirements in `manifest.yaml`:
```yaml
toolbelt:
  required:
    - name: "custom-tool"
      command: "tool"
      description: "Custom build tool"
      version: ">=1.0"
      install:
        windows: "winget install tool"
        macos: "brew install tool"
        linux: "apt install tool"
```

## 🔌 Port Management

mem8 includes a global port leasing system to prevent port conflicts when AI agents create multiple projects on the same machine.

### Quick Start
```bash
# Lease port range for current project
mem8 ports --lease

# View assigned ports
mem8 ports

# Kill process on a port (safe - only kills ports in your range)
mem8 ports --kill 20000

# List all port leases across all projects
mem8 ports --list-all

# Release ports when done
mem8 ports --release
```

### Key Features

**Global Registry:** `~/.mem8/port_leases.yaml` tracks all port leases across projects
- Prevents Next.js/React dev servers from conflicting (3000, 3001...)
- AI agents reference `.mem8/ports.md` for assigned port ranges
- Cross-platform port killing with `psutil` (no npx kill-port needed)

**Project-Specific Config:** `.mem8/ports.md` documents port assignments
- Simple range-based system (e.g., 20000-20004)
- AI agents choose any port within the range
- Instructions for Next.js, FastAPI, Docker, etc.

**Safe Port Killing:**
- By default, only kills ports within project's leased range
- Use `--force` to override safety check
- Cross-platform support (Windows, Mac, Linux)

### Example Workflow
```bash
# Project A
cd ~/projects/nextjs-app
mem8 ports --lease               # Gets 20000-20004
PORT=20000 npm run dev          # Uses assigned port

# Project B
cd ~/projects/api-server
mem8 ports --lease               # Gets 20005-20009
uvicorn main:app --port 20005   # No conflicts!
```

### Configuration Files

**`.mem8/ports.md`** - Project-specific port documentation
- Auto-generated with port range and usage examples
- Editable markdown section preserved on regeneration
- AI agents read this for port assignments

**`~/.mem8/port_leases.yaml`** - Global port registry
```yaml
leases:
  /path/to/project-a:
    project_name: nextjs-app
    start_port: 20000
    port_count: 5
    leased_at: '2025-10-07 01:28:43'
last_updated: '2025-10-07 01:28:43'
```

**`.mem8/config.yaml`** - Project configuration
```yaml
templates:
  default_source: "killerapp/mem8#subdir=mem8/templates"
```

## 🔄 Development Workflow

mem8 provides a structured inner loop for effective development:

### The Research → Plan → Implement → Commit Cycle

1. **Research** (`/research_codebase`) - Understand existing patterns and architecture
   - Uses parallel sub-agents for comprehensive codebase analysis
   - Creates timestamped research documents with metadata
   - Integrates findings from both code and memory repository

2. **Plan** (`/create_plan`) - Design your approach with concrete steps
   - Structured implementation plans with technical details
   - Clear requirements analysis and integration points  
   - Breaks down complex features into actionable tasks

3. **Implement** (`/implement_plan`) - Execute with progress tracking
   - Follows approved plans while adapting to reality
   - Updates progress with todo lists and checkboxes
   - Verification at natural stopping points

4. **Validate** (`/validate_plan`) - Verify implementation completeness
   - Systematic checking against original plan
   - Automated verification (build, tests, linting)
   - Recommendations for missing or incomplete work

5. **Commit** (`/commit`) - Create atomic, well-documented commits
   - Reviews session changes and creates logical groupings
   - Focuses on "why" rather than just "what" changed
   - Maintains clean git history

### Benefits
- **Thorough Understanding**: Research first reduces bugs and technical debt
- **Clear Direction**: Plans provide roadmap before coding begins  
- **Progress Tracking**: Todo lists and validation prevent incomplete work
- **Quality Commits**: Thoughtful commit messages improve team communication

### Getting Started
After running `mem8 init`, these commands are available in Claude Code as `/research_codebase`, `/create_plan`, etc. The workflow works best when following the sequence, but individual commands can be used as needed.

## 📋 Templates

### Claude Code Configuration (`claude-config`)
Generates `.claude/CLAUDE.md` with:
- Project-specific instructions
- Custom agents and commands
- Memory management settings
- Development workflows

**Example Usage:**
```bash
mem8 init --template claude-config
# Creates: .claude/CLAUDE.md, commands/, agents/
```

### Memory Repository (`memory-repo`)  
Creates structured documentation with:
- Research document templates
- Planning frameworks
- Decision logs
- Shared memory structure

**Example Usage:**
```bash
mem8 init --template memory-repo  
# Creates: memory/shared/, memory/research/, etc.
```

## 🎛️ Configuration

### Basic Setup
```bash
# Initialize in existing project
cd your-project
mem8 init --template claude-config

# Customize the generated .claude/CLAUDE.md
# Add project-specific instructions and workflows
```

### Advanced Configuration
```bash
# Use custom cookiecutter configs
mem8 init --template claude-config --config-file custom-config.yaml

# Link shared memory across projects
mem8 sync --link-shared ~/shared-memory
```

## 💻 Web Interface (Optional)

The mem8 web interface provides a browser-based viewer for your workspace:

### Features
- Browse research and planning documents
- Search across all markdown files  
- View file contents with syntax highlighting
- Navigate between different thought categories

### Setup Options

#### Quick Start (Development)
```bash
# Install dependencies and start the web interface
cd frontend && npm install && npm run dev
# Access at http://localhost:22211
```

#### Docker Compose (Full Stack)
```bash
# Start all services (frontend, backend, database)
docker-compose up -d

# Services available at:
# - Frontend: http://localhost:22211
# - Backend API: http://localhost:8000
# - PostgreSQL: localhost:5432
```

**Note:** The web interface is a simple file viewer - no authentication or database required.

## 🔧 Project Structure

```
your-project/
├── .claude/
│   ├── CLAUDE.md          # Main Claude Code configuration
│   ├── commands/          # Custom commands
│   └── agents/           # Custom agent definitions
├── memory/
│   ├── shared/           # Shared documentation
│   ├── research/         # Research documents
│   └── plans/           # Implementation plans
└── mem8-config.yaml     # mem8 workspace settings
```

## 👥 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development setup instructions.

**Quick Links:**
- 🐛 [Report Issues](https://github.com/killerapp/mem8/issues)
- 💬 [Discussions](https://github.com/killerapp/mem8/discussions)
- 🔧 [Development Guide](CONTRIBUTING.md)
- 🐳 [Docker Setup](DOCKER.md)

## 🛠️ Advanced Usage

### Search Functionality
```bash
# Full-text search
mem8 search "authentication"

# Search in specific directories
mem8 search "API" --path memory/shared/research

# Search with filters
mem8 search "bug" --tags "urgent" --type "plans"
```

### Sync and Sharing
```bash
# Sync with shared directory
mem8 sync

# Create symlinks to shared memory
mem8 sync --link ~/team-shared-memory

# Check sync status
mem8 status --verbose
```

### Custom Templates
```bash
# Create new template from existing project
mem8 template create my-template --from .

# Use custom template
mem8 init --template ./my-custom-template
```

## 📚 Integration with Claude Code

### Custom Agents
Place agent definitions in `.claude/agents/`:
```markdown
# .claude/agents/researcher.md
You are a research assistant focused on technical documentation...
```

### Custom Commands  
Add commands in `.claude/commands/`:
```bash
# .claude/commands/analyze.sh
#!/bin/bash
echo "Analyzing codebase structure..."
```

### Workspace Memory
Configure in `.claude/CLAUDE.md`:
```markdown
# Project Context
- Use `memory/research/` for background research
- Store implementation plans in `memory/plans/`
- Document decisions in `memory/decisions/`
```

## 🚀 Production Deployment

### Quick Start with Docker
```bash
# Build and start all services
docker-compose up -d

# Test the deployment (Windows PowerShell)
./test-docker.ps1

# Test the deployment (Linux/Mac)
./test-docker.sh

# Services will be available at:
# - Frontend: http://localhost:22211
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### API Server (Requires Docker)
The `mem8 serve` command starts the FastAPI backend server. **This requires a database (PostgreSQL or SQLite) which is provided via Docker:**

```bash
# Start backend with Docker (recommended)
docker-compose --env-file .env.dev up -d backend db

# The backend is now available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/api/v1/health
```

**Why Docker is required:**
- Backend needs PostgreSQL database for teams, memory, and authentication
- Docker Compose provides the full stack (backend + database + optional frontend)
- See [DOCKER.md](DOCKER.md) for all deployment options

### Docker Deployment Options

#### Production Stack (docker-compose.prod.yml)
```bash
# Start full production stack
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend  # API logs
docker-compose -f docker-compose.prod.yml logs -f frontend # Frontend logs

# Stop services
docker-compose -f docker-compose.prod.yml down

# Clean up (removes volumes)
docker-compose -f docker-compose.prod.yml down -v
```

#### Development Stack (with Hot Reloading)
```bash
# Start development environment with hot-reload enabled
docker-compose --env-file .env.dev up -d --build

# Frontend and backend will auto-reload on code changes
# View logs: docker-compose --env-file .env.dev logs -f
```

### Architecture
The production deployment uses:
- **mem8 serve**: FastAPI backend with unified CLI entry point
- **PostgreSQL**: Primary database for storing memory and metadata
- **Redis**: Cache layer and websocket support
- **Next.js**: Frontend application on port 22211

## 🧰 Requirements

- **Python 3.8+** - For mem8 CLI
- **uv** - Package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Node.js 18+** - For optional web interface
- **Git** - For sync functionality

## 🔄 Workflow Examples

### Research & Planning
```bash
# Start new research
mem8 init --template memory-repo
cd memory/research
# Create research-topic.md

# Plan implementation  
cd ../plans
# Create implementation-plan.md

# Search for related work
mem8 search "similar feature" --type research
```

### Claude Code Customization
```bash
# Set up Claude Code for new project
cd my-new-project  
mem8 init --template claude-config

# Customize .claude/CLAUDE.md with:
# - Project-specific context
# - Custom agent definitions  
# - Development workflows

# Test configuration
claude-code --help
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Focus areas:
1. **New Templates** - Create templates for different project types
2. **CLI Enhancements** - Improve search and sync functionality
3. **Web Interface** - Enhance the memory file viewer
4. **Documentation** - Improve setup and usage guides

---
*Designed for developers using Claude Code to enhance AI-assisted development workflows.*
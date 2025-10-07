# Contributing to mem8

Thank you for your interest in contributing to mem8! This guide will help you get set up for development.

## Prerequisites

- **Python 3.11+** - For mem8 CLI and backend
- **uv** - Package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Node.js 18+** - For frontend development (if working on web UI)
- **Docker Desktop** - For backend/teams development (required for database)
- **Git** - For version control

## Development Setup

### Choose Your Development Path

#### Path 1: CLI-Only Development

**Best for:** Working on CLI commands, search, metadata, worktree management

```bash
# Clone the repository
git clone https://github.com/killerapp/mem8.git
cd mem8

# Install mem8 CLI with all dependencies
uv tool install --editable .[server]

# Verify installation
mem8 --version
mem8 status

# Run tests
uv run pytest
```

**What you can work on:**
- ✅ CLI commands (`mem8 status`, `mem8 search`, `mem8 find`, etc.)
- ✅ Template system and cookiecutter integration
- ✅ Git worktree management
- ✅ Metadata extraction
- ❌ Backend API features (requires Docker)
- ❌ Team collaboration features (requires Docker)

---

#### Path 2: Full-Stack Development (Backend + Frontend)

**Best for:** Working on backend API, teams, authentication, database features

```bash
# Clone the repository
git clone https://github.com/killerapp/mem8.git
cd mem8

# 1. Install CLI dependencies
uv tool install --editable .[server]

# 2. Start Docker services (backend + database + frontend)
docker-compose --env-file .env.dev up -d --build

# 3. View logs to verify everything started
docker-compose logs -f

# Services available at:
# - Frontend: http://localhost:22211
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - PostgreSQL: localhost:5433
```

**What you can work on:**
- ✅ All CLI features
- ✅ Backend API endpoints
- ✅ Team collaboration features
- ✅ Authentication and authorization
- ✅ Database models and migrations
- ✅ Frontend UI components

**Making Backend Changes:**
The backend container has hot reload enabled. Changes to Python files in `backend/src/` will automatically restart the server.

**Making Frontend Changes:**
The frontend container has hot reload enabled with file polling (works on Windows). Changes to files in `frontend/` will automatically refresh.

---

#### Path 3: Hybrid Development (Backend Docker + Frontend Native)

**Best for:** Frontend development with faster refresh times

```bash
# Clone the repository
git clone https://github.com/killerapp/mem8.git
cd mem8

# 1. Start only backend services (backend + database)
docker-compose --env-file .env.dev up -d backend db

# 2. Install and run frontend natively
cd frontend
npm install
npm run dev

# Services available at:
# - Frontend: http://localhost:22211 (native npm)
# - Backend API: http://localhost:8000 (Docker)
# - API Docs: http://localhost:8000/docs
```

**Why this approach:**
- ⚡ Faster frontend hot reload (no Docker overhead)
- 🛠️ Native Node.js debugging tools
- 🔧 Direct access to node_modules for troubleshooting
- 🐳 Backend still properly containerized with database

---

## Project Structure

```
mem8/
├── mem8/                      # CLI source code
│   ├── cli/                  # CLI commands and interface
│   │   ├── main.py          # Main CLI entry point
│   │   ├── commands/        # Command implementations
│   │   └── types.py         # CLI type definitions
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration management
│   │   ├── search.py        # Search implementation
│   │   └── templates.py     # Template system
│   └── __init__.py          # Package initialization
│
├── backend/                  # Backend API (FastAPI)
│   ├── src/
│   │   └── mem8_api/
│   │       ├── main.py      # FastAPI application
│   │       ├── config.py    # API configuration
│   │       ├── database.py  # Database setup
│   │       ├── models/      # SQLAlchemy models
│   │       └── routers/     # API endpoints
│   ├── Dockerfile           # Production backend
│   └── requirements.txt     # Backend dependencies
│
├── frontend/                 # Frontend UI (Next.js)
│   ├── app/                 # Next.js app directory
│   ├── components/          # React components
│   ├── lib/                 # Utility functions
│   ├── Dockerfile           # Production frontend
│   ├── Dockerfile.dev       # Development frontend
│   └── package.json         # Frontend dependencies
│
├── .claude/                  # Claude Code configuration
│   ├── CLAUDE.md            # Project-specific instructions
│   ├── commands/            # Custom slash commands
│   └── agents/              # Custom agent definitions
│
├── thoughts/                 # Documentation and plans
│   └── shared/
│       ├── research/        # Research documents
│       ├── plans/           # Implementation plans
│       └── decisions/       # Technical decisions
│
├── docker-compose.yml        # Development Docker Compose
├── docker-compose.prod.yml   # Production Docker Compose
├── .env.dev                  # Development environment
├── .env.prod                 # Production environment
├── pyproject.toml            # Python package configuration
└── README.md                 # Project overview
```

---

## Making Changes

### CLI Development

1. Make changes to files in `mem8/`
2. Changes are immediately available (editable install)
3. Test your changes: `mem8 <command>`
4. Run tests: `uv run pytest`

### Backend Development

1. Make changes to files in `backend/src/mem8_api/`
2. Server auto-reloads on file changes (Docker development mode)
3. Test API endpoints: http://localhost:8000/docs
4. View logs: `docker-compose logs -f backend`

### Frontend Development

**Docker mode:**
1. Make changes to files in `frontend/`
2. Frontend auto-reloads on file changes
3. View at: http://localhost:22211

**Native mode:**
1. Make changes to files in `frontend/`
2. Frontend auto-reloads instantly
3. View at: http://localhost:22211

---

## Testing

### CLI Tests
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_cli.py

# Run with coverage
uv run pytest --cov=mem8
```

### Backend Tests
```bash
# Run backend tests
cd backend
uv run pytest

# With coverage
uv run pytest --cov=mem8_api
```

### Frontend Tests
```bash
cd frontend
npm run test
```

---

## Code Style

### Python
- Use **Black** for formatting: `uv run black mem8/`
- Use **isort** for imports: `uv run isort mem8/`
- Follow PEP 8 conventions
- Type hints encouraged

### TypeScript/JavaScript
- Use **ESLint**: `npm run lint`
- Follow Airbnb style guide
- Prefer functional components with hooks

---

## Commit Messages

We use **Conventional Commits** for automated releases:

```bash
# Features
feat: add team collaboration API endpoints

# Bug fixes
fix: resolve search indexing issue

# Documentation
docs: update API documentation

# Refactoring
refactor: extract CLI commands to separate modules

# Tests
test: add integration tests for search

# Chores
chore: update dependencies
```

**Important:** Commits trigger automated releases:
- `feat:` → Minor version bump (2.5.0 → 2.6.0)
- `fix:` → Patch version bump (2.5.0 → 2.5.1)
- `BREAKING CHANGE:` → Major version bump (2.5.0 → 3.0.0)

---

## Submitting Changes

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/my-feature`
3. **Make changes** following code style guidelines
4. **Write tests** for new functionality
5. **Commit** with conventional commit messages
6. **Push** to your fork: `git push origin feature/my-feature`
7. **Create a Pull Request** on GitHub

### Pull Request Checklist

- [ ] Tests pass locally (`uv run pytest`)
- [ ] Code follows style guidelines (Black, ESLint)
- [ ] Commit messages follow Conventional Commits
- [ ] Documentation updated if needed
- [ ] Tested in development environment

---

## Getting Help

- **Issues**: https://github.com/killerapp/mem8/issues
- **Discussions**: https://github.com/killerapp/mem8/discussions
- **Documentation**: [README.md](README.md) and [DOCKER.md](DOCKER.md)

---

## Development Tips

### Debugging Backend
```bash
# View backend logs
docker-compose logs -f backend

# Access backend container
docker-compose exec backend bash

# Check database
docker-compose exec db psql -U mem8_user -d mem8
```

### Debugging Frontend
```bash
# View frontend logs
docker-compose logs -f frontend

# Access frontend container
docker-compose exec frontend sh

# Native debugging (hybrid mode)
cd frontend
npm run dev  # Opens debugger port
```

### Rebuilding Containers
```bash
# Rebuild everything
docker-compose --env-file .env.dev up -d --build

# Rebuild specific service
docker-compose --env-file .env.dev up -d --build backend
```

### Database Migrations
```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head
```

---

Thank you for contributing to mem8! 🚀

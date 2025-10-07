# mem8 Developer Quick Reference

## Installation & Setup

```bash
# Install CLI with all dependencies
uv tool install --editable .[server]

# Verify installation
mem8 --version
mem8 status
```

## Development Paths

### 🎯 Path 1: CLI-Only Development
**No Docker needed** - Work on CLI commands, search, templates

```bash
# Install and use CLI directly
uv tool install --editable .
mem8 status
mem8 search "query"
mem8 find plans
```

**What works without Docker:**
- ✅ All `mem8` CLI commands
- ✅ Search and find operations
- ✅ Template initialization
- ✅ Git worktree management
- ✅ Metadata extraction
- ❌ Backend API (`mem8 serve`)
- ❌ Team features

---

### 🎯 Path 2: Full-Stack Development
**Docker required** - Backend API, teams, database features

```bash
# Start all services
docker-compose --env-file .env.dev up -d --build

# View logs
docker-compose logs -f

# Services:
# - Frontend: http://localhost:22211
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - PostgreSQL: localhost:5433
```

**What runs in Docker:**
- ✅ Backend FastAPI server (with hot reload)
- ✅ PostgreSQL database
- ✅ Frontend Next.js (with hot reload)
- ✅ All source code mounted for live editing

---

### 🎯 Path 3: Hybrid Development
**Best for frontend work** - Backend in Docker, Frontend native

```bash
# Start backend services only
docker-compose --env-file .env.dev up -d backend db

# Run frontend natively
cd frontend
npm install
npm run dev

# Frontend: http://localhost:22211 (native)
# Backend: http://localhost:8000 (Docker)
```

**Why this is useful:**
- ⚡ Faster frontend refresh
- 🛠️ Native Node.js debugging
- 🔧 Direct npm access
- 🐳 Backend properly containerized

---

## Quick Commands

### Docker Operations
```bash
# Start all services
docker-compose --env-file .env.dev up -d

# Start backend only
docker-compose --env-file .env.dev up -d backend db

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild
docker-compose --env-file .env.dev up -d --build

# Stop
docker-compose down

# Clean up
docker-compose down -v  # Removes volumes too
```

### Testing
```bash
# CLI tests
uv run pytest

# Backend tests
cd backend && uv run pytest

# Frontend tests
cd frontend && npm test
```

### Code Quality
```bash
# Python formatting
uv run black mem8/
uv run isort mem8/

# Frontend linting
cd frontend && npm run lint
```

---

## Project Structure

```
mem8/
├── mem8/                    # CLI source
│   ├── cli/                # Commands & interface
│   └── core/              # Core functionality
├── backend/                # FastAPI backend
│   └── src/mem8_api/      # API implementation
├── frontend/               # Next.js frontend
│   ├── app/               # Pages & routes
│   └── components/        # React components
├── .claude/                # Claude Code config
├── thoughts/              # Documentation
└── docker-compose.yml     # Development stack
```

---

## Environment Files

- **`.env.dev`** - Development (PostgreSQL on 5433)
- **`.env.prod`** - Production template
- **`.env`** - Local overrides (gitignored)

---

## Common Issues

### "mem8 serve" fails with database error
**Solution:** Backend requires Docker
```bash
docker-compose --env-file .env.dev up -d backend db
```

### Frontend not refreshing in Docker
**Solution:** Uses polling for Windows - may have slight delay
- Switch to hybrid mode for faster refresh

### Port already in use
**Solution:** Check running containers
```bash
docker ps
docker-compose down
```

---

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python package config & dependencies |
| `docker-compose.yml` | Development Docker setup |
| `docker-compose.prod.yml` | Production Docker setup |
| `mem8/cli/main.py` | CLI entry point |
| `backend/src/mem8_api/main.py` | Backend entry point |
| `frontend/app/page.tsx` | Frontend homepage |

---

## Additional Documentation

- 📘 [README.md](README.md) - Project overview
- 🐳 [DOCKER.md](DOCKER.md) - Docker setup details
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - Full contributing guide

---

## Getting Help

- **Issues**: https://github.com/killerapp/mem8/issues
- **Discussions**: https://github.com/killerapp/mem8/discussions

---

**Quick Start Cheatsheet:**

```bash
# CLI only
uv tool install --editable .

# Full stack
docker-compose --env-file .env.dev up -d

# Frontend dev
docker-compose --env-file .env.dev up -d backend db
cd frontend && npm run dev
```

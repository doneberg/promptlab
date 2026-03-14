# PromptLab

PromptLab is a backend-first AI workflow dashboard that allows users to define structured, multi-step AI workflows and execute them with dynamic runtime variables.

It separates workflow definitions from execution history, providing traceable and reproducible AI runs.

---

## Features

- JWT-based authentication
- Create and manage workflows
- Add ordered prompt blocks with Jinja-style variables (`{{ variable }}`)
- Execute workflows asynchronously
- Immutable execution history
- Per-step:
  - Rendered prompt
  - AI response
  - Latency tracking
  - Execution status (pending → running → completed/failed)
- Secure per-user data isolation

---

## Architecture

Layered backend design:

```
Routes → Services → Domain Models → Infrastructure
```

Core model:

```
User
  └── Workflows
         └── PromptBlocks

WorkflowExecution
  └── ExecutionSteps
```

Execution is immutable and stored independently from workflow definitions.

AI integration is abstracted behind a provider interface, allowing vendor swapping without changing execution logic.

---

## Tech Stack

**Backend**
- FastAPI (async)
- SQLAlchemy (async ORM)
- SQLite (development)
- JWT (python-jose)
- bcrypt password hashing
- Jinja2 template rendering
- BackgroundTasks for async execution

**Frontend**
- Vanilla JavaScript
- Fetch API
- JWT stored in localStorage
- Polling-based execution updates

---

## Running Locally

### Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Runs on: `http://127.0.0.1:8000`

### Frontend

```bash
cd frontend
python -m http.server 3000
```

Runs on: `http://localhost:3000`

PromptLab is designed as a foundation for a scalable AI workflow platform.
# FArmor - Intent-Aware Payment Executor (Hackathon Build)

FArmor is a full demo system that separates:
- reasoning (`backend/reasoning.py`)
- enforcement (`backend/enforcement.py`)
- execution (`backend/execution.py`)

It includes a premium frontend and a backend API with demonstration scenarios.

## Project Structure

- `backend/models.py` - strict `Intent` and `Policy` schemas
- `backend/reasoning.py` - LLM-style intent parsing from text to `Intent`
- `backend/enforcement.py` - deterministic policy firewall + `PolicyViolationError`
- `backend/execution.py` - writes real `receipts/receipt_*.txt` files
- `backend/server.py` - HTTP server and API routes
- `main.py` - CLI demo with 3 mandatory test cases
- `frontend/` - complete UI
- `data/policies.json` - policy definitions
- `docs/architecture.md` - architecture diagram
- `docs/short-report.md` - submission short report

## Run Backend + Frontend

```bash
cd /home/aryan/Farmor
python3 -m backend.server
```

Open: `http://127.0.0.1:8080`

## Run CLI Demo Cases

```bash
cd /home/aryan/Farmor
python3 main.py
```

This runs:
1. Allowed action
2. Blocked action (limit violation)
3. Delegation boundary violation

## API Quick Test

```bash
curl -s -X POST http://127.0.0.1:8080/api/execute \
  -H "Content-Type: application/json" \
  -d '{"policy_name":"default","request_text":"I am the DevOps Bot, pay $400 to AWS for hosting."}'
```

## Why This Fits The Hackathon Rules

- Clear reasoning vs execution separation
- Explicit runtime policy enforcement
- Deterministic blocking with visible reasons
- Real local system side effect (receipt files)
- Includes bounded delegation scenario

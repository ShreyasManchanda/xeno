# Xeno — AI-native CRM

This repository contains the Xeno project: a FastAPI backend (backend/), a delivery-simulator channel service (channel-service/), and a Next.js frontend (frontend/). The codebase includes an agent pipeline (backend/agents/) and test suites under `tests/`.

**Quick links**
- **Backend**: [backend](backend)
- **Channel service**: [channel-service](channel-service)
- **Frontend**: [frontend](frontend)
- **Tests**: [tests](tests)

**Requirements**
- Git
- Python 3.11+ (recommended)
- Node 18+ and npm or pnpm

Getting started (local)
- Clone the repo:

  ```powershell
  git clone https://github.com/ShreyasManchanda/xeno.git
  cd xeno
  ```

- Backend (local dev):

  ```powershell
  cd backend
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  # run the app
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ```

- Frontend (local dev):

  ```powershell
  cd frontend
  npm install
  npm run dev
  # open http://localhost:3000
  ```

- Channel-service (local dev):

  ```powershell
  cd channel-service
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port 8001 --reload
  ```


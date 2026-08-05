# Repository Guidelines

## Project Structure & Module Organization

The application lives in `hakimi-erp/`. Backend routes are in `backend/app/api/v1/endpoints/`, SQLAlchemy models in `app/models/`, Pydantic schemas in `app/schemas/`, and business logic in `app/services/`. SQL setup lives in `backend/database/`. Vue source is organized under `frontend/src/` into `views/`, `components/`, `layout/`, `api/`, `constants/`, and `utils/`. Treat `design_specs/` and `refer_docs/` as authoritative for workflows, UI behavior, API contracts, and data definitions.

## Build, Test, and Development Commands

Run the full Windows development stack from `hakimi-erp/`:

```powershell
.\start-hakimi.ps1
```

This prepares backend dependencies and starts the API on port 8000 and Vite on port 5173. To run services separately:

```powershell
cd hakimi-erp\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe server.py

cd ..\frontend
npm ci
npm run dev
npm run build
npm run preview
```

`npm run build` is the required frontend compilation check; `preview` serves the production bundle locally.

## Coding Style & Naming Conventions

Use four-space indentation and `snake_case` in Python, database fields, and API payloads. Use two-space indentation and `camelCase` in TypeScript; name Vue components in `PascalCase` and constants in `SCREAMING_SNAKE_CASE`. Keep endpoints thin, domain logic in services, and cross-module orchestration in `services/flows/`. Reuse `frontend/src/constants/` instead of hard-coding shared values. No formatter or linter is configured, so match adjacent files.

## Testing Guidelines

No automated test runner or coverage threshold is configured. Before submitting, run `npm run build`, exercise changed routes through `/api/v1/openapi.json`, and verify affected MySQL workflows. Place new backend tests in `backend/tests/test_*.py` and frontend tests in `frontend/src/__tests__/*.spec.ts`. Document any new test dependency.

## Commit & Pull Request Guidelines

This snapshot has no Git history, but `design_specs/DEVELOPMENT_SPEC.md` requires `feat:`, `fix:`, `docs:`, or `refactor:` prefixes. Develop on `feature/<name>` branches and target `frontend` or `backend` before integration into `dev`. PRs need a behavior summary, linked issue, validation steps, and one reviewer. Include UI screenshots and identify database or API-contract changes.

## Security & Configuration

Copy `backend/.env.example` to `backend/.env`; keep credentials local. Never commit `.env`, virtual environments, dependencies, logs, or generated bundles. Coordinate API or schema changes with documentation and frontend consumers.

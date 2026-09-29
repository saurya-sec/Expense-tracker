# Ledger Frontend

React + TypeScript + Vite frontend wired to the FastAPI contract supplied with this project.

## Run

```bash
npm install
cp .env.example .env
npm run dev
```

Windows PowerShell:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Set `VITE_API_BASE_URL` to your FastAPI origin, for example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API coverage

Implemented:

- `GET /`
- `GET /health/db`
- `POST /auth/signup`
- `POST /auth/login`
- `GET /income`
- `POST /income`
- `GET /income/{income_id}`
- `PUT /income/{income_id}`
- `DELETE /income/{income_id}`
- `GET /expenses`
- `POST /expenses`
- `GET /expenses/{Expense_id}`
- `PUT /expenses/{Expense_id}`
- `DELETE /expenses/{Expense_id}`
- `POST /chat` with `Authorization: Bearer <access_token>`
- `POST /esewa/upload` multipart field `file`
- `POST /statement/upload` multipart field `file`

The UI does not generate fake records or fake successful responses. HTTP errors, validation errors, and network errors are surfaced to the user.

## Important backend observations from the supplied OpenAPI export

The supplied run showed:

1. `POST /auth/signup` returned HTTP 500.
2. `POST /statement/upload` returned HTTP 500 for the tested XLS file with:
   `Failed to import statement: No /Root object! - Is this really a PDF?`
3. `GET /health/db` returned HTTP 500 in the supplied run.
4. `POST /esewa/upload` returned a structured success payload.

Those are backend issues; the frontend is intentionally wired to expose them instead of masking them.

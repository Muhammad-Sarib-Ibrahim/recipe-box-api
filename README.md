# Recipe Box API

A small REST API for managing personal recipes, built with FastAPI. Users register, log in,
and get a JWT token that authorizes them to create, read, update, and delete their own recipes.
Other users' recipes are fully inaccessible — even knowing a recipe's ID isn't enough.

Built as a learning/portfolio project to practice backend fundamentals: auth, ORM models vs.
API schemas, dependency injection, and automated testing.

## Stack

- **FastAPI** — web framework
- **SQLModel** (SQLAlchemy + Pydantic) — ORM and validation
- **SQLite** — zero-setup local database
- **bcrypt** — password hashing
- **python-jose** — JWT creation/verification
- **pytest** — automated tests (7 passing, covering auth, ownership checks, and CRUD)

## Setup

```bash
git clone <this-repo>
cd recipe-api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be running at `http://localhost:8000`. Interactive docs (Swagger UI) are at
`http://localhost:8000/docs` — you can register, log in, and try every endpoint directly
from the browser.

## Running tests

```bash
pytest tests/ -v
```

Tests run against an isolated in-memory database, so they never touch your local `recipes.db`.

## Example usage

```bash
# Register
curl -X POST localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# Log in (returns a JWT)
curl -X POST localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# Create a recipe (use the token from login)
curl -X POST localhost:8000/recipes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"title": "Pasta", "ingredients": "pasta, tomato, garlic", "instructions": "Boil. Mix. Eat."}'

# List your recipes
curl localhost:8000/recipes -H "Authorization: Bearer <your-token>"
```

## Project structure

```
app/
├── database.py      # DB engine and session setup
├── models.py         # SQLModel table definitions
├── schemas.py        # Pydantic request/response shapes (kept separate from
│                      #   DB models so e.g. password hashes never leak in responses)
├── auth.py            # password hashing, JWT creation/verification
├── main.py            # FastAPI app setup
└── routers/
    ├── auth.py         # /auth/register, /auth/login
    └── recipes.py      # /recipes CRUD, with per-user ownership checks
tests/
└── test_api.py         # auth flow, ownership enforcement, full CRUD lifecycle
```

## Design notes

- Recipe ownership is enforced server-side: trying to access or modify someone else's
  recipe returns a `404`, not a `403`, so the API doesn't even reveal that the recipe exists.
- `ingredients` is stored as a plain string rather than a normalized ingredients table —
  a deliberate scope decision to keep the data model simple for a small project.
- Passwords are hashed with bcrypt before storage; plaintext passwords are never persisted
  or logged.

## Possible extensions

- Pagination and search/filter on `GET /recipes`
- Dockerfile for one-command setup
- PostgreSQL instead of SQLite for production use

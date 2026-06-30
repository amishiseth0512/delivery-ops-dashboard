# Delivery Ops Dashboard — Setup Guide

This guide takes you from a fresh machine to a running FastAPI server connected to PostgreSQL.

---

## 1. Install PostgreSQL (if you don't have it)

### macOS (recommended: Homebrew)
```bash
brew install postgresql@16
brew services start postgresql@16
```

After starting, verify it's running:
```bash
psql --version
```

### Windows
Download and run the installer from https://www.postgresql.org/download/windows/
During installation, note the password you set for the `postgres` user — you'll need it below.

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

---

## 2. Create the database

Open a PostgreSQL shell:
```bash
# macOS / Linux
psql -U postgres

# If the above fails on macOS, try:
psql postgres
```

Inside the shell, run:
```sql
CREATE DATABASE delivery_ops;
-- Verify it was created:
\l
-- Exit the shell:
\q
```

---

## 3. Set up your Python environment

From the project root (`delivery-ops-dashboard/`):

```bash
# Create a virtual environment (keeps dependencies isolated from your system Python)
python3 -m venv venv

# Activate it
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows (Command Prompt)
# venv\Scripts\Activate.ps1     # Windows (PowerShell)

# Install all dependencies
pip install -r requirements.txt
```

---

## 4. Configure your environment variables

Copy the example file and fill in your PostgreSQL password:

```bash
cp .env.example .env
```

Open `.env` and set the connection string:
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/delivery_ops
```

**Connection string breakdown:**
- `postgres` — the PostgreSQL username (default)
- `yourpassword` — the password you set during installation
- `localhost:5432` — host and default port
- `delivery_ops` — the database name you created in step 2

---

## 5. Run the server

```bash
uvicorn app.main:app --reload
```

- `app.main` — refers to the file `app/main.py`
- `:app` — refers to the FastAPI instance named `app` inside that file
- `--reload` — restarts the server automatically when you edit a file (great for development)

On first startup, SQLAlchemy will automatically create the three tables (`users`, `orders`, `order_status_history`) in your database.

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

---

## 6. Explore the API

FastAPI generates interactive documentation automatically. Open your browser to:

- **Swagger UI** (try requests in-browser): http://127.0.0.1:8000/docs
- **ReDoc** (cleaner read-only reference): http://127.0.0.1:8000/redoc

### Quick test with curl

```bash
# Create a dispatcher user
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "password": "secret123", "role": "dispatcher"}'

# Create a driver user
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "email": "bob@example.com", "password": "secret456", "role": "driver"}'

# List all users (passwords are never returned)
curl http://127.0.0.1:8000/users/

# Create an order assigned to Bob (driver id=2)
curl -X POST http://127.0.0.1:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{"description": "Deliver package to 123 Main St", "driver_id": 2}'

# List all orders
curl http://127.0.0.1:8000/orders/

# Get one order
curl http://127.0.0.1:8000/orders/1
```

---

## Project structure explained

```
delivery-ops-dashboard/
├── app/
│   ├── main.py        — FastAPI app; registers routes; creates DB tables on startup
│   ├── database.py    — SQLAlchemy engine and session factory; get_db() dependency
│   ├── models.py      — ORM table definitions (User, Order, OrderStatusHistory)
│   ├── schemas.py     — Pydantic shapes for request bodies and JSON responses
│   └── routes/
│       ├── orders.py  — GET /orders, GET /orders/{id}, POST /orders
│       └── users.py   — GET /users, POST /users
├── .env               — your local secrets (git-ignored)
├── .env.example       — template committed to git
├── requirements.txt   — Python dependencies
└── SETUP.md           — this file
```

### Why two kinds of models?

| | SQLAlchemy models (`models.py`) | Pydantic schemas (`schemas.py`) |
|---|---|---|
| **Purpose** | Map Python classes to DB tables | Validate and shape JSON in/out |
| **Lives in** | `app/models.py` | `app/schemas.py` |
| **Used by** | `db.query(models.Order)` | `response_model=`, request body |
| **Talks to** | PostgreSQL | HTTP client |

---

## What's next (Step 2)

- JWT authentication — login endpoint that issues tokens
- Role-based access — dispatchers create orders; drivers update status
- The `order_status_history` table gets populated automatically on status changes

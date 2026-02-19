# Inventory & Order Management System

FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL · Alembic · Docker

---

## Quick Start

```bash
cp .env.example .env
docker-compose up --build
```

The entrypoint waits for PostgreSQL, runs `alembic upgrade head`, then starts uvicorn.

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

---

## Frontend

The UI is a React + Vite app located in `frontend/`. It connects to the backend API at `http://localhost:8000`.

**Prerequisites:** Node.js 18+. The backend must be running first (`docker-compose up` or local uvicorn).

```bash
cd frontend
npm install
npm run dev
```

UI available at `http://localhost:5173`.

---

## Project Structure

```
app/
├── main.py              # App factory, exception handlers
├── config.py            # Settings via pydantic-settings
├── database.py          # Async engine, session factory, Base
├── dependencies.py      # get_db() DI
├── exceptions.py        # Domain exception hierarchy
├── models/              # ORM models (Product, Order, OrderItem)
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic (OrderService, ProductService)
└── api/v1/              # Route handlers (/products, /orders)
alembic/versions/        # Database migrations
tests/                   # Integration test suite
scripts/entrypoint.sh    # Docker entrypoint
```

---

## API Endpoints

| Method  | Path                          | Status | Description             |
|---------|-------------------------------|--------|-------------------------|
| `POST`  | `/api/v1/products`            | 201    | Create product          |
| `GET`   | `/api/v1/products`            | 200    | List products (paginated) |
| `POST`  | `/api/v1/orders`              | 201    | Create order            |
| `GET`   | `/api/v1/orders/{id}`         | 200    | Get order with items    |
| `PATCH` | `/api/v1/orders/{id}/status`  | 200    | Update order status     |
| `GET`   | `/health`                     | 200    | Health check            |

Status transitions: `Pending → Shipped`, `Pending → Cancelled`. Shipped and Cancelled are terminal.

---

## Running Tests

**Via Docker (recommended):**

```bash
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

**Locally:**

```bash
pip install -r requirements.txt
export TEST_ASYNC_DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/test_inventory_db"
psql -U user -c "CREATE DATABASE test_inventory_db;"
pytest tests/ -v --tb=short
```

---

## Local Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # update DB credentials
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Design Notes

**Concurrency - SELECT FOR UPDATE:**  
Order creation locks product rows with `SELECT ... FOR UPDATE` (ordered by `product_id` to prevent deadlocks). This ensures two concurrent requests cannot both observe the same stock value and both succeed - the second transaction blocks until the first commits. Pessimistic locking was chosen over optimistic (version columns) because it provides a correctness guarantee without retry logic on the caller side, which matters when overselling has direct business consequences.

**price_at_time:**  
`OrderItem` stores a price snapshot at creation time. Product price changes do not affect historical orders.

**DB-level constraint:**  
`CHECK (stock_quantity >= 0)` on the products table is a last-resort guard even if application logic has a bug.

**Two database DSNs:**  
Alembic does not support asyncpg natively, so `DATABASE_URL` (psycopg2) is used for migrations and `ASYNC_DATABASE_URL` (asyncpg) for the application.

**Trade-offs:**

| Decision | Chosen | Alternative |
|---|---|---|
| Locking | Pessimistic (FOR UPDATE) | Optimistic (version column) |
| Loading | selectin | joinedload (unsupported async) |
| Test isolation | Per-test table drop/create | Savepoint rollback |
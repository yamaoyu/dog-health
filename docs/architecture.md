# Architecture

---

# Frontend

* Vue 3
* TypeScript
* Composition API
* Feature-based directory structure

Example:

frontend/src/features/dogs
frontend/src/features/events

---

# Backend

* FastAPI
* SQLAlchemy
* Alembic for migrations
* REST API

---

# Database

PostgreSQL is used as the primary database.

Initial tables:

* owners
* dogs
* owner_dogs

Future plan:

* events

---

# Event Design

This section is future scope.
Events are stored in a single table.

Initial event types:

* meal
* walk
* medicine
* toilet
* hospital
* memo

Custom event types are out of scope for MVP.

---

# Authentication

Authentication is intentionally simplified for MVP.

Initial implementation:

* owner selection
* temporary login without password

Future plan:

* JWT authentication

---

# Development Environment

All services run with Docker Compose.

Containers:

* frontend
* backend
* db

# Directory structure
## backend
Service/repository layers are intentionally omitted during MVP phase.

alembic/
app/
　├ routers/
　├ models/
　├ schemas/
　├ db/
　├ config.py
　├ main.py
tests/

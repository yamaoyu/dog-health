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
* events
* event_types
* walk_events
* food_events
* toilet_events

---

# Event Design

Events use a common `events` table plus event-specific detail tables.

Initial event types:

* walk
* food
* toilet

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
Repository layers are introduced only where DB branching would make routers too large.

alembic/
app/
　├ routers/
　├ models/
　├ schemas/
　├ db/
　├ config.py
　├ main.py
tests/

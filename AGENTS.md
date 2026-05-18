# Project Rules

## Architecture

* frontend and backend must stay separated
* keep API contracts explicit
* prefer simple architecture
* avoid over abstraction
* prefer maintainability over theoretical scalability
* if the current approach becomes too complex, stop and propose a simpler alternative
* ask before introducing major dependencies
* prefer explicit/simple code over clever abstractions

※ 過剰な abstraction や generic 化は禁止

---

## Frontend

* Vue 3 + TypeScript
* use composition API
* use Pinia only when needed
* avoid unnecessary service layers

※ state 管理は必要になるまで増やさない

---

## Backend

* FastAPI
* validate all input with Pydantic
* keep services simple
* keep routers thin
* avoid premature abstraction
* avoid unnecessary service layers

※ service layer の増殖を避ける

---

## Security

* validate auth boundaries
* sanitize user input
* never expose secrets

---

## Workflow

* explain implementation plan first
* always run tests
* MVP first

※ 実装前に必ず plan を説明する

---

## Comments
* avoid obvious comments
* explain WHY, not WHAT

---

## docker
* avoid unnecessary infrastructure complexity

---

## Naming
* Python uses snake_case
* Vue components use PascalCase
* composables start with use*

## Coding Rules

* avoid hardcoded configuration values
* use environment variables for ports, URLs, and secrets
* prefer explicit configuration management

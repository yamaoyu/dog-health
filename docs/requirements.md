# Overview

Personal learning project for AI-assisted development.

This application helps dog owners track:

* daily health condition
* meals
* medications
* symptoms
* vet visits
* walk history

The project focuses on:

* maintainable architecture
* simple implementation
* explicit frontend/backend separation
* Docker-based development
* iterative MVP development

---

# Technical Constraints

* Vue 3 + TypeScript
* FastAPI
* PostgreSQL
* Docker Compose

---

# Architecture Principles

* maintainability over scalability
* avoid over abstraction
* MVP first
* simple relational data modeling
* backend-driven API design

---

# Domain Concepts

## Owners

Owners can manage multiple dogs.

## Dogs

Dogs can belong to multiple owners.

## Events

Dog activities are stored as events.

Examples:

* meal
* walk
* medicine
* symptoms
* hospital
* memo

Event types are initially fixed for simplicity.

---

# Current MVP Scope

## Goal

Create a minimal but functional dog health tracking application.

## Included

* owner management　(create and get)
* dog management (create and get)
* owner-dog relationship

## Not Included

* event recording
* event history view
* authentication
* notifications
* analytics
* AI diagnosis
* custom event types
* admin dashboard
* production infrastructure

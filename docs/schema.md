# Database Schema

---

# owners

Represents dog owners.

| column     | type      | notes         | null          |
| ---------- | --------- | ------------- | ------------- |
| owner_id   | uuid      | primary key   | No            |
| name       | text      | display name  | No            |
| login_id   | text      | login id      | No            |

owner_id is used to system
The login ID is used to identify users, and each user can choose their own ID.

---

# dogs

Represents dogs.

| column     | type      | notes         | null          |
| ---------- | --------- | ------------- | ------------- |
| dog_id     | uuid      | primary key   | no            |
| name       | text      | dog name      | no            |
| birthday   | date      |               | yes           |
| gender     | text      | allowed: 'male', 'female', 'unknown'| yes           |

---

# owner_dogs

Many-to-many relation between owners and dogs.

| column     | type      | notes              | null          |
| ---------- | --------- | ------------------ | ------------- |
| owner_dog_id | uuid    | primary key        | no            |
| owner_id   | uuid      | FK owners.owner_id | no            |
| dog_id     | uuid      | FK dogs.dog_id     | no            |
| role       | text      | optional           | yes           |

Constraints:

* UNIQUE(owner_id, dog_id)

---

# Planned Tables

## events

Dog activities and health logs.

Status:

planned for future MVP phase.

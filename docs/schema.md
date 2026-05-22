# Database Schema

---

# owners

Represents dog owners.

| column     | type      | notes         |
| ---------- | --------- | ------------- |
| owner_id   | uuid      | primary key   |
| name       | text      | display name  |
| login_id   | text      | login id      |

owner_id is used to system
The login ID is used to identify users, and each user can choose their own ID.

---

# dogs

Represents dogs.

| column     | type      | notes         |
| ---------- | --------- | ------------- |
| dog_id     | uuid      | primary key   |
| name       | text      | dog name      |
| birthday   | date      | necessary     |

---

# owner_dogs

Many-to-many relation between owners and dogs.

| column     | type      | notes              |
| ---------- | --------- | ------------------ |
| owner_dog_id | uuid    | primary key        |
| owner_id   | uuid      | FK owners.owner_id |
| dog_id     | uuid      | FK dogs.dog_id     |
| role       | text      | optional           |

Constraints:

* UNIQUE(owner_id, dog_id)

---

# Planned Tables

## events

Dog activities and health logs.

Status:

planned for future MVP phase.

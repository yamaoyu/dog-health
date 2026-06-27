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

# event_types

Master data for supported event types.

| column        | type    | notes             | null |
| ------------- | ------- | ----------------- | ---- |
| event_type_id | uuid    | primary key       | no   |
| code          | text    | unique event code | no   |
| display_name  | text    | display label     | no   |
| is_active     | boolean | selectable or not | no   |

Initial event types:

* walk
* food
* toilet

---

# events

Common dog event records.

| column        | type        | notes                        | null |
| ------------- | ----------- | ---------------------------- | ---- |
| event_id      | uuid        | primary key                  | no   |
| dog_id        | uuid        | FK dogs.dog_id               | no   |
| event_type_id | uuid        | FK event_types.event_type_id | no   |
| occurred_at   | timestamptz | event time                   | no   |
| memo          | text        | optional note                | yes  |

---

# walk_events

Details for walk events.

| column   | type | notes                  | null |
| -------- | ---- | ---------------------- | ---- |
| event_id | uuid | PK, FK events.event_id | no   |
| distance | text | optional distance      | yes  |
| time     | text | optional duration      | yes  |

---

# food_events

Details for food events.

| column   | type | notes                  | null |
| -------- | ---- | ---------------------- | ---- |
| event_id | uuid | PK, FK events.event_id | no   |
| menu     | text | optional menu          | yes  |
| amount   | text | optional amount        | yes  |

---

# toilet_events

Details for toilet events.

| column    | type | notes                  | null |
| --------- | ---- | ---------------------- | ---- |
| event_id  | uuid | PK, FK events.event_id | no   |
| type      | text | optional type          | yes  |
| condition | text | optional condition     | yes  |

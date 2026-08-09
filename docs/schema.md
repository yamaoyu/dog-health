# データベーススキーマ

---

# owners

犬の飼い主を表す。

| column     | type      | 備考          | null          |
| ---------- | --------- | ------------- | ------------- |
| owner_id   | uuid      | primary key   | no            |
| name       | text      | 表示名         | no            |
| login_id   | text      | login id      | no            |

owner_id は system 内部で使用する。
login ID は user 識別に使用し、各 user が自分で決められる。

---

# dogs

犬を表す。

| column     | type      | 備考          | null          |
| ---------- | --------- | ------------- | ------------- |
| dog_id     | uuid      | primary key   | no            |
| name       | text      | 犬の名前       | no            |
| birthday   | date      |               | yes           |
| gender     | text      | 許可値: 'male', 'female', 'unknown'| yes           |

---

# owner_dogs

owner と dog の多対多関係を表す。

| column     | type      | 備考               | null          |
| ---------- | --------- | ------------------ | ------------- |
| owner_dog_id | uuid    | primary key        | no            |
| owner_id   | uuid      | FK owners.owner_id | no            |
| dog_id     | uuid      | FK dogs.dog_id     | no            |
| role       | text      | 任意               | yes           |

制約:

* UNIQUE(owner_id, dog_id)

---

# event_types

対応している event type のマスタデータ。

| column        | type    | 備考              | null |
| ------------- | ------- | ----------------- | ---- |
| event_type_id | uuid    | primary key       | no   |
| code          | text    | 一意な event code | no   |
| display_name  | text    | 表示ラベル         | no   |
| is_active     | boolean | 選択可能かどうか   | no   |

初期 event type:

* walk
* food
* toilet

---

# events

犬の event に共通するレコード。

| column        | type        | 備考                         | null |
| ------------- | ----------- | ---------------------------- | ---- |
| event_id      | uuid        | primary key                  | no   |
| dog_id        | uuid        | FK dogs.dog_id               | no   |
| event_type_id | uuid        | FK event_types.event_type_id | no   |
| occurred_at   | timestamptz | event 発生日時               | no   |
| memo          | text        | 任意メモ                     | yes  |

---

# walk_events

walk event の詳細。

| column           | type         | 備考                                       | null |
| ---------------- | ------------ | ------------------------------------------ | ---- |
| event_id         | uuid         | PK, FK events.event_id                     | no   |
| distance_km      | numeric(4,1) | 任意の距離（km）、最大 10.0                 | yes  |
| duration_minutes | integer      | 任意の時間（分）                            | yes  |

---

# food_events

food event の詳細。

| column       | type    | 備考                               | null |
| ------------ | ------- | ---------------------------------- | ---- |
| event_id     | uuid    | PK, FK events.event_id             | no   |
| menu         | text    | 任意のメニュー                     | yes  |
| amount_grams | integer | 任意の量（g）、最大 1000            | yes  |

---

# toilet_events

toilet event の詳細。

| column    | type | 備考                   | null |
| --------- | ---- | ---------------------- | ---- |
| event_id  | uuid | PK, FK events.event_id | no   |
| type      | text | 任意の type            | yes  |
| condition | text | 任意の condition       | yes  |

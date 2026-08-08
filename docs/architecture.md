# アーキテクチャ

---

# フロントエンド

* Vue 3
* TypeScript
* Composition API
* feature-based なディレクトリ構成

例:

frontend/src/features/dogs
frontend/src/features/events

---

# バックエンド

* FastAPI
* SQLAlchemy
* migration には Alembic を使う
* REST API

---

# データベース

主要な database として PostgreSQL を使う。

初期 table:

* owners
* dogs
* owner_dogs
* events
* event_types
* walk_events
* food_events
* toilet_events

---

# Event 設計

event は共通の `events` table と、event ごとの詳細 table を使う。

初期 event type:

* walk
* food
* toilet

custom event type は MVP のスコープ外とする。

---

# 認証

MVP では認証を意図的に簡略化する。

初期実装:

* owner 選択
* password なしの一時 login

将来方針:

* JWT 認証

---

# 開発環境

すべての service は Docker Compose で実行する。

container:

* frontend
* backend
* db

# ディレクトリ構成
## backend
DB 分岐によって router が大きくなりすぎる場合に限り、repository layer を導入する。

alembic/
app/
　├ routers/
　├ models/
　├ schemas/
　├ db/
　├ config.py
　├ main.py
tests/

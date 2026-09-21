# アーキテクチャ

このドキュメントは、dog-healthの技術構造を管理する。プロダクト目的とMVPスコープは `docs/requirements.md`、実装規約は `docs/coding-standards.md` を参照する。

## 技術スタック

- フロントエンド: Vue 3 + TypeScript + Vite
- バックエンド: FastAPI
- ORM: SQLAlchemy
- migration: Alembic
- database: PostgreSQL
- 開発環境: Docker Compose

## 基本方針

- フロントエンドとバックエンドを分離する。
- API契約を明確にする。
- シンプルなアーキテクチャを優先する。
- 拡張性より保守性を優先する。
- 過剰な抽象化を避ける。
- バックエンド主導でAPIを設計する。
- シンプルなリレーショナルデータモデリングを優先する。

## API契約

開発中はFastAPIが生成するSwagger UI（`/docs`）とOpenAPI schema（`/openapi.json`）で、現在のAPIの入出力や使用例を確認する。

APIの実際の入力条件と動作はPydantic schema、validator、routerの実装とテストで確認する。OpenAPIに表れない条件もあるため、Swagger UIだけで全ての制約を判断しない。機能別要件には、画面が利用するAPIとユーザーから見た期待動作を記載する。

APIを変更するときは、バックエンドのschemaとテスト、フロントエンドの型と利用箇所を同時に確認する。Swagger UIでの説明や使用例は、実際の動作と一致するように保つ。

## フロントエンド

Vue 3、TypeScript、Composition APIを使う。

feature-basedなディレクトリ構成を基本にする。

例:

- `frontend/src/features/dogs`
- `frontend/src/features/events`

状態管理は必要になるまで増やさない。Piniaは必要になった場合だけ導入する。

## バックエンド

FastAPI、SQLAlchemy、Alembicを使う。

ルーターは薄く保つ。入力はPydantic schemaで検証する。

DB分岐によってrouterが大きくなりすぎる場合に限り、repository layerを導入する。理論上の拡張性のためだけにlayerを増やさない。

基本構成:

```text
backend/
  alembic/
  app/
    routers/
    models/
    schemas/
    db/
    config.py
    main.py
  tests/
```

## データベース

主要なdatabaseとしてPostgreSQLを使う。schemaの詳細は `docs/schema.md` を参照する。

初期table:

- `owners`
- `dogs`
- `owner_dogs`
- `events`
- `event_types`
- `walk_events`
- `food_events`
- `toilet_events`

## Event設計

eventは共通の `events` tableと、eventごとの詳細tableを使う。

初期event type:

- `walk`
- `food`
- `toilet`

custom event typeはMVPのスコープ外とする。

## 認証

MVPでは認証を意図的に簡略化する。

初期実装:

- owner選択
- passwordなしの一時login

将来方針:

- JWT認証

## 開発環境

すべてのserviceはDocker Composeで実行する。

container:

- `frontend`
- `backend`
- `db`

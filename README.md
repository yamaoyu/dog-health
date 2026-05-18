# dog-health

frontend / backend / db を分離した、シンプルな初期構成です。

## 構成

- `frontend`: Vue 3 + TypeScript + Vite
- `backend`: FastAPI
- `db`: Docker Compose 管理の PostgreSQL

## 使用ポート

- frontend: `5180`
- backend: `8010`
- postgres: `5500`

## 起動方法

### Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

起動後の確認先:

- frontend: `http://localhost:5180`
- backend health check: `http://localhost:8010/health`

## コンテナ内テスト

```bash
docker compose run --rm --build backend python -m pytest
```

## API

- `GET /health`: アプリケーションの状態と現在の DB 設定を返します

## 補足

- backend はルーティングと設定を明示的に保ち、現時点では service layer を設けていません。
- DB 接続は、実際に永続化処理が必要になるまでは環境変数ベースの最小構成に留めています。
- `/health` では backend から PostgreSQL への実接続確認も行います。
- 運用方針は container-first です。backend の依存関係はローカルではなくイメージ内にのみインストールします。
- frontend は `http://localhost:5180` と `http://127.0.0.1:5180` の両方から backend へ接続できるようにしています。

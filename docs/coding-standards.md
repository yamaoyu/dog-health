# コーディング規約

このドキュメントは、実装時に守る具体的なコード規約を管理する。プロジェクト全体の最上位ルールは `AGENTS.md`、開発フローは `docs/development.md` を参照する。

## 基本方針

- シンプルで明示的なコードを優先する。
- 巧妙な抽象化より読みやすさを優先する。
- 早すぎる最適化を避ける。
- 必要になるまで状態管理、service layer、repository layerを増やさない。
- 現在の方針が複雑になりすぎる場合は、いったん止めてよりシンプルな代案を提示する。

## 命名

- Pythonは `snake_case` を使う。
- Vue componentは `PascalCase` を使う。
- composableは `use*` で始める。
- database table nameは `snake_case` の複数形にする。
- primary keyは `{table_singular}_id` にする。

例:

- `dogs.dog_id`
- `owners.owner_id`

## コメント

- 自明なコメントは避ける。
- 何をしているかではなく、なぜそうしているかを説明する。

## 設定

- 設定値の直書きを避ける。
- port、URL、secretは環境変数を使う。
- 明示的な設定管理を優先する。
- secret、token、passwordをコード、ログ、ドキュメントに露出しない。

## フロントエンド

- Vue 3 + TypeScriptを使う。
- Composition APIを使う。
- feature-basedなディレクトリ構成にする。
- Piniaは必要な場合だけ使う。
- 不要なservice layerは避ける。
- API callは専用のservice fileに置く。
- system向けではなく、ユーザーに見せるべき情報だけを表示する。

## フロントエンドテスト

- フロントエンドのtestにはVitestを使う。
- ユーザー操作をテストする場合、viewには統合テスト形式のtestを書く。
- view testは各featureの `views` ディレクトリに置く。

例:

- `frontend/src/features/auth/views/LoginView.spec.ts`

Testing Libraryのqueryは次の順で優先する。

1. `getByRole`
2. `getByLabelText`
3. `getByText`

accessible role、label、textで合理的に選択できない場合だけ `data-testid` を使う。

## バックエンド

- FastAPIを使う。
- すべての入力をPydanticで検証する。
- ルーターは薄く保つ。
- serviceはシンプルに保つ。
- 不要なservice layerは避ける。
- DB分岐によってrouterが大きくなりすぎる場合に限り、repository layerを導入する。

## API

- resource nameは複数形にする。
- 動詞ベースのendpointは避ける。

良い例:

- `/owners`
- `/dogs`
- `/owner-dogs`

悪い例:

- `/createDog`
- `/getDogs`

HTTP methodは次の用途で使う。

- `GET`: 取得
- `POST`: 作成
- `PUT`: 全体更新
- `PATCH`: 部分更新
- `DELETE`: 削除

## SQLAlchemy

- declarative modelを使う。
- modelはシンプルに保つ。
- 不要なrepository layerは避ける。

## Docker

- 不要なインフラの複雑性を避ける。
- 開発環境はDocker Composeを基本にする。

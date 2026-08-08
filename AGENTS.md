# プロジェクトルール

## 言語
日本人のみがこのプロジェクトに参加しているため日本語とする

## アーキテクチャ

* フロントエンドとバックエンドは分離する
* API 契約は明確にする
* シンプルなアーキテクチャを優先する
* 過剰な抽象化は避ける
* 理論上の拡張性より保守性を優先する
* 現在の方針が複雑になりすぎる場合は、いったん止めてよりシンプルな代案を提案する
* 大きな依存関係を追加する前に確認する
* 巧妙な抽象化より、明示的でシンプルなコードを優先する

※ 過剰な抽象化や汎用化は禁止

---

## フロントエンド

* Vue 3 + TypeScript
* Composition API を使う
* Pinia は必要な場合だけ使う
* 不要なサービス層は避ける

※ 状態管理は必要になるまで増やさない

---

## バックエンド

* FastAPI
* すべての入力を Pydantic で検証する
* サービスはシンプルに保つ
* ルーターは薄く保つ
* 早すぎる抽象化は避ける
* 不要なサービス層は避ける

※ サービス層の増殖を避ける

---

## セキュリティ

* 認証境界を検証する
* ユーザー入力を無害化する
* secret を絶対に露出しない

---

## ワークフロー

* 先に実装計画を説明する
* 常にテストを実行する
* MVP を優先する

※ 実装前に必ず計画を説明する

---

## コメント
* 自明なコメントは避ける
* 何をしているかではなく、なぜそうしているかを説明する

---

## docker
* 不要なインフラの複雑性を避ける

---

## 命名
* Python は snake_case を使う
* Vue component は PascalCase を使う
* composable は use* で始める

## コーディングルール

* 設定値の直書きは避ける
* port、URL、secret は環境変数を使う
* 明示的な設定管理を優先する

## 基本方針

* 実装はシンプルに保つ
* 抽象化より読みやすさを優先する
* MVP を優先する
* 早すぎる最適化は避ける

---

## バックエンドの規約

### API 命名

resource name は複数形にする。

例:

* /owners
* /dogs
* /owner-dogs

動詞ベースの endpoint は避ける。

悪い例:

* /createDog
* /getDogs

---

### HTTP メソッド

* GET: 取得
* POST: 作成
* PUT: 更新（全体更新）
* PATCH: 部分更新
* DELETE: 削除

---

### Database 命名

* table name は snake_case の複数形にする
* primary key は {table_singular}_id にする

例:

* dogs.dog_id
* owners.owner_id

---

### SQLAlchemy

* declarative model を使う
* model はシンプルに保つ
* 不要な repository layer は避ける

---

## フロントエンドの規約

* feature-based なディレクトリ構成にする
* Composition API を使う
* API call は専用の service file に置く
* system 向けではなく、ユーザーに見せるべき情報だけを表示する

---

## スコープ管理

明示的に依頼されない限り、以下は実装しない:

* 認証
* 分析
* 通知
* admin 機能

## フロントエンドテスト

* フロントエンドの test には Vitest を使う
* ユーザー操作をテストする場合、view には統合テスト形式の test を書く
* view test は各 feature の `views` ディレクトリに置く
  * 例: `frontend/src/features/auth/views/LoginView.spec.ts`
* Testing Library の query は次の順で優先する:
  1. `getByRole`
  2. `getByLabelText`
  3. `getByText`
* accessible role、label、text で合理的に選択できない場合だけ `data-testid` を使う
* button click や API call の検証など、ユーザー視点の振る舞いをテストする

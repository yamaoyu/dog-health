# 開発手順

このドキュメントは、Harness EngineeringでAIと開発を進めるときの運用ルールを管理する。具体的なコード規約は `docs/coding-standards.md`、プロダクト要件は `docs/requirements.md`、技術構造は `docs/architecture.md` を参照する。

## ドキュメントの役割

- `AGENTS.md`: Codexが毎回守る最上位ルールと参照先。
- `GLOSSARY.md`: コード、要件、会話で共通して使うドメイン用語。
- `docs/adr/`: 後から変更しにくい設計判断と、その選択理由。
- `docs/requirements.md`: プロダクト目的、MVPスコープ、機能別要件への入口。
- `docs/requirements/`: 画面、操作、期待動作を含む機能別要件。
- `docs/architecture.md`: フロントエンド、バックエンド、DB、認証、開発環境の技術構造。
- `docs/coding-standards.md`: 命名、API、DB、テスト、コメント、設定などの実装規約。
- `docs/schema.md`: database schemaの詳細。
- `docs/testing.md`: 変更内容に応じたテストと検証の選び方。

## Harness Engineeringの流れ

1. 要求が曖昧な場合は `grill-with-docs` Skillで整理し、確定した用語や設計判断を `GLOSSARY.md` またはADRへ記録する。
2. `create-issue` SkillでGitHub Issueを作成する。
3. `start-issue` SkillでIssue、関連docs、既存コード、テストを確認し、実装計画を説明する。
4. 振る舞いの変更には `tdd` Skill、不具合の原因調査には `diagnosing-bugs` Skillを必要に応じて使って実装する。
5. 関連するテスト、型チェック、ビルドを実行する。
6. `code-review` Skillで規約とIssueの2軸から差分を確認する。
7. 問題があれば修正し、必要な検証とレビューを再実行する。
8. `create-pr` Skillで差分、検証結果、関連Issueを確認してDraft PRを作成する。
9. 開発環境に改善を反映すべき学びがある場合は `retro` Skillで振り返る。

要求や変更が小さく明確な場合は、目的に不要なSkillを省略してよい。

## Issue作成ルール

Issueは実装単位で作成する。原則として、1つのIssueは1つの目的に集中したPRに収まる大きさにする。

Issueに含める内容:

- 背景・現状
- 対象範囲
- 対象外
- 受け入れ条件
- 検証方法
- 実装上の補足

Issueに含めない内容:

- 複数PRにまたがる大きすぎる作業
- 調査していない実装方法の推測
- 明示的に依頼されていない認証、分析、通知、admin機能

## 実装開始前の確認

実装前に次を確認する。

- 対象Issueの目的、対象範囲、対象外
- `AGENTS.md`
- 関連する `docs/`
- 既存の関連コード
- 既存の関連テスト
- API、DB、画面の契約に影響があるか
- APIに影響する場合、Swagger UIまたはOpenAPI schemaの説明や使用例が実際の動作と一致するか
- 追加依存が必要か

実装方針が複雑になりすぎる場合は、作業を止めてシンプルな代案を提示する。

## PR作成前の確認

PR作成前に次を確認する。

- `git status --short --branch`
- 差分全体
- 関連Issueの受け入れ条件を満たしているか
- 関係のない変更が含まれていないか
- `code-review` Skillによるレビューが完了しているか
- 実行した検証と結果
- 実行できなかった検証と理由

PRは原則としてDraft PRで作成する。

## コードレビュー

実装と関連検証が終わったら、PR作成前に `code-review` Skillを使い、次の2軸を分けて確認する。

- 規約: `AGENTS.md`、コーディング規約、関連ADRに適合しているか。
- 仕様: 関連Issueの受け入れ条件を満たし、対象外の変更を含んでいないか。

指摘を修正した場合は、影響する検証とレビューを再実行する。

## 用語集とADRの更新

- 用語の意味や境界が変わる場合は `GLOSSARY.md` を更新する。
- 後から変更するコストが高く、背景なしでは意図が分かりにくく、実際のトレードオフを伴う判断はADRへ記録する。
- 実装方法、入力条件、作業手順はGlossaryやADRへ重複させず、要件、Issue、Skillへ記録する。

## 検証方針

変更内容に応じて必要な検証を選ぶ。詳細は `docs/testing.md` を参照する。実行していない検証を成功したものとして扱わない。

### フロントエンド変更

`frontend/` で実行する。

- `npm run type-check`
- `npm test`
- ビルドやバンドルに影響する場合は `npm run build`

### バックエンド変更

`backend/` で実行する。

- `python -m pytest`

### ドキュメントのみの変更

- Markdownの内容を目視確認する。
- リンク先ファイルが存在することを確認する。
- 主要ルールの移動や削除が意図通りであることを `rg` などで確認する。
- アプリコードに差分がないことを確認する。

### Skill変更

- `SKILL.md` のfrontmatterに `name` と `description` があることを確認する。
- Skill名が lowercase letters、digits、hyphens のみであることを確認する。
- 可能であれば `codex debug prompt-input` などでCodexから認識できることを確認する。

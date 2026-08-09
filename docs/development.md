# 開発手順

このドキュメントは、Harness EngineeringでAIと開発を進めるときの運用ルールを管理する。具体的なコード規約は `docs/coding-standards.md`、プロダクト要件は `docs/requirements.md`、技術構造は `docs/architecture.md` を参照する。

## ドキュメントの役割

- `AGENTS.md`: Codexが毎回守る最上位ルールと参照先。
- `docs/requirements.md`: プロダクト目的、MVPスコープ、機能別要件への入口。
- `docs/architecture.md`: フロントエンド、バックエンド、DB、認証、開発環境の技術構造。
- `docs/coding-standards.md`: 命名、API、DB、テスト、コメント、設定などの実装規約。
- `docs/schema.md`: database schemaの詳細。

## Harness Engineeringの流れ

1. ユーザーの要求を整理する。
2. `create-issue` SkillでGitHub Issueを作成する。
3. Issueの範囲、対象外、受け入れ条件、検証方法を確認する。
4. 実装計画を説明する。
5. 関連するdocs、既存コード、テストを確認する。
6. 実装する。
7. 関連するテスト、型チェック、ビルドを実行する。
8. セルフレビューを行う。
9. 問題があれば修正し、必要な検証を再実行する。
10. `create-pr` Skillで差分、検証結果、関連Issueを確認してDraft PRを作成する。

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
- 追加依存が必要か

実装方針が複雑になりすぎる場合は、作業を止めてシンプルな代案を提示する。

## PR作成前の確認

PR作成前に次を確認する。

- `git status --short --branch`
- 差分全体
- 関連Issueの受け入れ条件を満たしているか
- 関係のない変更が含まれていないか
- セルフレビューが完了しているか
- 実行した検証と結果
- 実行できなかった検証と理由

PRは原則としてDraft PRで作成する。

## セルフレビュー

実装と関連検証が終わったら、PR作成前にセルフレビューを行う。セルフレビュー用Skillは別途作成する。将来のSkill名は `self-review` を想定する。

セルフレビューでは次を確認する。

- 関連Issueを読む。
- `docs/requirements.md` と関連する要件ドキュメントを読む。
- `AGENTS.md` を確認する。
- `git diff` 全体を確認する。
- Issueの受け入れ条件を1つずつ確認する。
- バグ、回帰、境界条件を確認する。
- 過剰実装がないか確認する。
- 不要な抽象化がないか確認する。
- テスト不足を確認する。
- docs更新漏れを確認する。
- 問題があれば修正する。
- 修正後に必要なテストを再実行する。
- 問題がなくなるまで再確認する。

## 検証方針

変更内容に応じて必要な検証を選ぶ。実行していない検証を成功したものとして扱わない。

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

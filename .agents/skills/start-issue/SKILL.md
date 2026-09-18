---
name: start-issue
description: この dog-health リポジトリでGitHub Issueの実装を開始する前に、Issue確認、関連docsと関連コードの調査、実装計画作成、ブランチ確認、検証方針整理を行う。Codex が実装に着手する前の準備を標準化し、計画提示までで止める必要がある場合に使う。
---

# Issue 開始

このSkillは、GitHub Issueを読んで実装を始める前の準備を標準化するために使う。

このSkillでは実装しない。Issue、docs、関連コード、現在のブランチを確認し、実装計画と検証方針をユーザーに提示して止まる。

## 手順

1. 対象Issue番号またはIssue URLを確認する。ユーザーの依頼から特定できない場合だけ、対象Issueを確認する。
2. GitHub MCP/GitHubコネクタを使ってIssueのタイトル、本文、コメント、ラベル、状態を確認する。利用できない場合は、Issue本文の共有をユーザーに依頼し、勝手に代替手段でIssueを変更しない。
3. Issueがclosedの場合は、実装開始前に止まり、続行してよいかユーザーに確認する。
4. Issueの目的、背景、対象範囲、対象外、作業項目、受け入れ条件、検証方法を整理する。
5. `AGENTS.md` を確認する。特に、日本語対応、実装前の計画説明、docs確認、secret非露出、MVP優先、過剰な抽象化回避、フロントエンド/バックエンド責務分離、検証実行のルールを守る。
6. 関連するdocsを確認する。最低限、`docs/development.md`、`docs/coding-standards.md`、`docs/requirements.md`、`docs/architecture.md`、`docs/schema.md` を読む。
7. Issueの内容に応じて追加docsを確認する。存在する場合は、`docs/requirements/`、`docs/api-contract.md`、`docs/testing.md`、関連するREADMEや設計メモも読む。
8. 関連するコード、テスト、設定、Issueテンプレート、CI、既存Skillを調査する。必要な範囲に絞り、実装に直接関係しない詳細調査を広げすぎない。
9. `git status --short --branch` を実行し、現在のブランチと未コミット変更を確認する。
10. 未コミット変更がある場合は、ブランチをcheckoutしない。自分の作業かユーザーの作業かを決めつけず、Issue対応に関係するかを確認する。関係ない変更は触らない。
11. Issue種別からブランチ種別を決める。機能追加は `feature`、ドキュメントは `docs`、リファクタリングは `refactor`、修正は `fix`、その他は `task` を使う。
12. ブランチ名は `<種別>_#<issue番号>_<修正概要>` とする。例: `docs_#13_prepare_ai_development_docs`。修正概要は短い英語のsnake_caseにする。
13. デフォルトブランチ上にいる場合、または現在のブランチ名がIssueに合っていない場合は、実装開始前に止まり、ブランチ作成または切り替え方針をユーザーに確認する。ただし未コミット変更がある場合はcheckoutしない。
14. Issueとdocsの間に矛盾がある場合、または対象範囲が大きすぎる場合は、実装計画を確定する前に懸念点と分割案を提示する。
15. 明示的に依頼されていない認証、分析、通知、admin機能、大きな依存関係、実アプリ外の仕組みを計画に含めない。
16. フロントエンド変更、バックエンド変更、DB変更、docs変更、Skill変更のどれが必要かを分類する。
17. 受け入れ条件を実装タスクに対応付ける。満たし方が曖昧な条件は、実装前に確認事項として整理する。
18. 検証方針を整理する。既存docsと設定から、実行すべきテスト、型チェック、ビルド、lint、手動確認を選ぶ。
19. 実装計画、変更予定ファイル、対象外、検証方針、確認事項をユーザーに提示する。
20. ユーザーが明示的に実装開始を依頼するまで、このSkillの流れではファイル変更を行わない。

## 調査対象

必ず確認するもの:

- `AGENTS.md`
- 対象Issue
- `docs/development.md`
- `docs/coding-standards.md`
- `docs/requirements.md`
- `docs/architecture.md`
- `docs/schema.md`
- `git status --short --branch`

Issue内容に応じて確認するもの:

- `docs/requirements/`
- `docs/api-contract.md`
- `docs/testing.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/workflows/`
- `frontend/package.json`
- `backend/requirements.txt`
- 関連するフロントエンド/バックエンドコード
- 関連するテスト
- 関連する既存Skill

## 実装計画の形式

ユーザーに提示する計画は、次の構造を基本にする。

```markdown
## Issue確認

- Issue: #<number> <title>
- 状態:
- 目的:
- 対象範囲:
- 対象外:

## 調査結果

- 関連docs:
- 関連コード:
- 既存テスト/検証:
- 制約・注意点:

## ブランチ状況

- 現在のブランチ:
- 推奨ブランチ名:
- 未コミット変更:
- 実装前に必要な対応:

## 実装計画

1.
2.
3.

## 検証方針

-

## 確認事項

-
```

確認事項がない場合は、`確認事項はありません。` と明記する。

## ブランチ命名

ブランチ名は `<種別>_#<issue番号>_<修正概要>` とする。

- 機能追加: `feature`
- ドキュメント: `docs`
- リファクタリング: `refactor`
- 修正: `fix`
- その他: `task`

例:

- `feature_#8_add_owner_registration`
- `docs_#13_prepare_ai_development_docs`
- `refactor_#21_simplify_owner_router`
- `fix_#34_handle_empty_dog_list`
- `task_#40_update_ci_settings`

未コミット変更がある場合は、ブランチをcheckoutしない。変更内容を確認し、退避、コミット、別worktreeなどの方針をユーザーに確認してから進める。

## 検証方針の選び方

- フロントエンド変更: `frontend/` で `npm run type-check` と `npm test` を候補にする。ビルドやバンドルに影響する場合は `npm run build` も候補にする。
- バックエンド変更: `backend/` で `python -m pytest` を候補にする。
- DB schema/migration変更: Alembic migration、関連pytest、schema docs更新確認を候補にする。
- docsのみの変更: Markdownの目視確認、リンク先ファイルの存在確認、`git diff` でアプリコードに差分がないことの確認を候補にする。
- Skill変更: `SKILL.md` のfrontmatter、Skill名、手順の妥当性、必要に応じたCodex認識確認を候補にする。

実行していない検証を成功したものとして扱わない。実装後に実行できない可能性がある検証は、理由と代替確認を計画に含める。

## ルール

- このSkillでは実装、コミット、push、PR作成を行わない。
- 実装開始前に計画を説明する。
- Issue本文より広い範囲を勝手に実装計画へ含めない。
- 対象外を明確にする。
- 大きな依存関係が必要になりそうな場合は、実装計画の段階でユーザーに確認する。
- secret、token、passwordなどの機密情報を出力しない。
- ユーザーの未コミット変更を上書き、削除、revertしない。

# 第三者ソフトウェア

このリポジトリは、次の第三者ソフトウェアを含む。

## Matt Pocock Skills

- 対象: `.agents/skills/` に配置したMatt Pocock由来のスキルと付属ファイル
- 取得元: [mattpocock/skills](https://github.com/mattpocock/skills)
- 上流コミット: [`5863806dd4e15c63174bee4e7515a4256792ecfa`](https://github.com/mattpocock/skills/commit/5863806dd4e15c63174bee4e7515a4256792ecfa)
- 著作権者: Copyright (c) 2026 Matt Pocock
- ライセンス: MIT License

ライセンス原文は [`licenses/mattpocock-skills-MIT.txt`](licenses/mattpocock-skills-MIT.txt) を参照する。

### ローカル変更

Codexとの互換性のため、次の最小限の変更を加えている。

- `grill-with-docs` と `retro`: Skill呼び出しを、依存する `SKILL.md` の直接参照へ置き換えた。
- `tdd`: 未導入の `codebase-design` 呼び出しを、既存コードを調査してインターフェースとテスト境界を合意する手順へ置き換えた。
- `code-review`: 未導入のセットアップSkillとtracker文書への依存を、GitHub MCP/GitHubコネクタによるIssue取得手順へ置き換えた。

その他の外部由来ファイルは原文のまま管理する。

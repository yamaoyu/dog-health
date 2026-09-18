# テスト・検証方針

このドキュメントは、変更内容に応じて必要なテストと検証を選ぶための基準を管理する。具体的な実装規約は `coding-standards.md`、開発の流れは `development.md` を参照する。

## 基本方針

- Issueの受け入れ条件と変更による回帰リスクをテスト対象にする。
- 実装詳細ではなく、外部から確認できる動作を優先する。
- 正常系だけでなく、入力境界、存在しないresource、重複、空の状態、API失敗を必要に応じて確認する。
- 既存テストで十分な場合は重複するテストを追加しない。
- 実行していない検証を成功したものとして扱わない。
- 実行できない検証がある場合は、理由と代替確認をIssueまたはPRに記載する。

## テストの責務

### Backend

pytestでAPIとdatabase modelを検証する。

- router testではrequest、response、status code、validation、永続化を確認する。
- repositoryを持つ機能では、routerとrepositoryの責務境界を保って検証する。
- database model testではtable名、column、constraint、relationがschemaと一致することを確認する。
- APIの契約はFastAPIが生成するOpenAPIを正とし、schemaまたはrouter変更時はSwagger UIまたは `/openapi.json` への反映も確認する。

配置:

- `backend/tests/test_<feature>_api.py`
- `backend/tests/test_models.py`

実行:

```bash
cd backend
python -m pytest
```

container-firstの環境では次を使う。

```bash
docker compose run --rm --build backend python -m pytest
```

### Frontend

VitestとTesting Libraryで、ユーザーから見た画面動作を検証する。

- view testは入力、ボタン操作、API呼び出し、表示、画面遷移をまとめた統合テストとする。
- API clientはmockし、送信payloadと画面側のresponse処理を確認する。
- loading、empty、success、validation error、API errorを変更範囲に応じて確認する。
- 非同期取得が競合し得る画面では、古いresponseが現在の表示を上書きしないことを確認する。
- 要素の取得は `getByRole`、`getByLabelText`、`getByText` の順で優先する。

配置:

- view: `frontend/src/features/<feature>/views/*.spec.ts`
- component固有の操作: 対象componentと同じfeature配下の `*.spec.ts`

実行:

```bash
cd frontend
npm run type-check
npm test
```

buildやbundle、環境変数の参照に影響する場合は、次も実行する。

```bash
npm run build
```

## 変更種別ごとの検証

| 変更 | 必須の候補 | 追加で確認すること |
| --- | --- | --- |
| Frontendの画面・component | `npm run type-check`、`npm test` | 主要操作の手動確認、必要なら`npm run build` |
| FrontendのAPI client | `npm run type-check`、`npm test` | OpenAPIとのmethod、path、payload、response型の一致 |
| Backendのrouter・schema | `python -m pytest` | Swagger UIまたは`/openapi.json`、status code、validation error |
| Backendのmodel・repository | `python -m pytest` | transaction、constraint、relation、既存データへの影響 |
| DB schema・migration | `python -m pytest`、migration適用確認 | upgrade順序、constraint、`docs/schema.md` |
| 複数層にまたがる機能 | FrontendとBackendの両方 | 実環境で代表的な一連の操作 |
| docsのみ | Markdown目視、リンク確認、`git diff --check` | アプリコードに差分がないこと |
| Skill | frontmatterと手順の確認 | Codexから認識できること |

「必須の候補」は変更内容を基に選択する。たとえば文言だけの変更で無関係なBackend testまで機械的に実行する必要はないが、省略理由を説明できるようにする。

## API変更時の確認

独立したAPI契約書は作成せず、OpenAPIを単一の情報源として扱う。APIを追加または変更するときは、次を確認する。

1. Pydantic schemaにrequest、response、validation ruleが表現されている。
2. routerにmethod、path、response model、成功時のstatus codeが定義されている。
3. 想定するerror responseがpytestで検証されている。
4. Swagger UIまたは `/openapi.json` に変更が反映されている。
5. FrontendのAPI client、TypeScript型、画面側のerror処理が契約と一致している。
6. 仕様上必要な説明がSwaggerから分からない場合は、schemaまたはendpointの説明を追加する。

## 手動確認

自動テストで保証しにくい次の内容は、変更範囲に応じて手動確認する。

- 画面遷移と一連のユーザーフロー
- responsive layout、modal、menuなどの見た目と操作性
- loading中の操作抑止
- 実Backendと接続したrequest・response
- Swagger UIでのAPI表示と試行
- timezoneや日付境界に依存する表示

## Issue・PRへの記録

検証結果には次を記載する。

- 実行したcommandまたは手動確認内容
- 成功・失敗の結果
- 実行しなかった検証と理由
- 既知の問題または今回の対象外

テストが成功していても、Issueの受け入れ条件を満たしているかは別途確認する。

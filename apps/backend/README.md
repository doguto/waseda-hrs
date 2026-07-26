# HRS Backend

ホテル予約システム（HRS）のバックエンド実装基盤です。授業課題で作成した
UMLのBCE（Boundary / Control / Entity）分類と、実装上の責務を対応させるため、
FastAPIアプリケーションと業務・DB処理をuv workspaceの別packageに分けています。

現時点では基盤のみを用意しており、APIは`GET /healthz`、SQLは疎通確認用の
`Ping`クエリだけを実装しています。

## 構成

```text
apps/backend/
├── packages/
│   ├── api/                        FastAPIとHTTP境界
│   │   └── src/api/
│   │       ├── api/                routes・request/response schema
│   │       ├── infrastructure/     FastAPIからDB等を組み立てる処理
│   │       ├── services/           dependency provider
│   │       └── main.py
│   └── libs/                       HTTPに依存しない処理
│       └── src/libs/
│           ├── domain/             Entity・値オブジェクト・業務ルール
│           ├── application/        ユースケースとトランザクション境界
│           └── infrastructure/db/
│               ├── gen/            sqlc生成コード
│               └── repositories/   DBアクセスのadapter
├── sqlc/
│   ├── query/backend/              sqlcが解析するSQL
│   ├── schema.sql                  DB schemaの唯一の正
│   └── sqlc.yaml
├── docker-compose.yaml
├── Makefile
└── pyproject.toml                  uv workspaceルート
```

UMLとの主な対応は次のとおりです。

| UMLの分類 | 実装 |
|---|---|
| `<<boundary>>` | `packages/api`のrouteとschema |
| `<<control>>` | `packages/libs/application`のユースケース |
| `<<entity>>` | `packages/libs/domain`のモデル |

## DBアクセス

DBはPostgreSQLを使用します。

- `schema.sql`をDB構造の正とする
- sqldefで現在のDBとの差分を適用する
- queryをSQLファイルとして記述する
- sqlcでSQLAlchemy向けの型付きPythonコードを生成する
- SQLAlchemyはORMではなく、Engine・Connection・connection pool・
  transaction管理に使用する
- 生成コードをRepositoryで包み、Application層からsqlcへ直接依存しない

この方式ではschemaとqueryをSQLとしてそのまま確認でき、SQLAlchemyのORMモデルと
`schema.sql`を二重管理せずに済みます。

sqlc生成コードは`packages/libs/src/libs/infrastructure/db/gen`に出力されます。
生成物は直接編集しないでください。

```bash
make sqlc
```

ローカルに`sqlc`がインストールされている場合はそのbinaryを使用します。
存在しない場合は`sqlc/go.mod`で固定した`go tool sqlc`を使用するため、
初回のみGoのコンパイルに数分かかることがあります。

## Schema migration

schemaの差分確認と適用は次のコマンドで行います。

```bash
make dry-migrate
make migrate
```

sqldefは宣言的schema管理であり、migration履歴やデータ変換手順を保持しません。
また、同じschemaを適用した後でもDDLを生成するphantom diffが起きると、
意図しないschema変更につながります。

そのためCIでは隔離したPostgreSQLに`schema.sql`を一度適用し、同じschemaで
再度dry-runして以下を検査します。

- `Run:`で始まるDDLがひとつも生成されない
- `-- Nothing is modified --`が出力される

## ローカル起動

APIとPostgreSQLはDocker Composeで起動できます。

```bash
docker compose up --build --wait
curl http://localhost:8080/healthz
```

API containerはPostgreSQLのhealthcheck完了後に起動します。API imageは
uvによるbuild stageとPython slimのruntime stageに分け、runtimeには構築済みの
仮想環境だけをコピーしています。

## デモデータと動作確認

新しいPostgreSQLボリュームを作成すると、デモ用にstandard (10,000円/泊)、
deluxe (16,000円/泊)、suite (25,000円/泊) の客室と料金が登録されます。

起動後、以下で予約、照会、チェックイン、チェックアウト、キャンセルの全5ユースケースを
API経由で確認できます。

```bash
python scripts/verify_api.py
```

すでに起動済みでデモデータがない場合は、ローカルのデモDBをリセットしてから再起動します。
この操作はローカルのPostgreSQLデータを削除します。

```bash
docker compose down -v
docker compose up --build --wait
```

## 開発用コマンド

```bash
uv sync --all-packages
make fmt
make check
```

`make check`はRuff、mypy、pytestを実行します。テスト未作成の現在だけは
pytestの「テストなし」を成功扱いにし、テスト失敗は通常どおりCIを失敗させます。

# HRS Frontend Workspace

ホテル予約システム（HRS）のデモ用フロントエンドです。[`apps/backend`](../backend)の
FastAPIを叩くSPAで、バックエンドが公開するOpenAPIから型を生成して型安全に通信します。

`apps/backend` がuv workspace + `packages/{api,libs}` であるのと同じく、
このディレクトリがpnpm workspaceのrootで、実体は `packages/*` に置いています。

## アクターごとにアプリを分ける

`docs/uml/08_bce_objects.md` はバウンダリを「**アクター×ユースケース**の組ごとに1つ」と
定めています。これに合わせ、利用者とフロント係でアプリ自体を分けています。

| パッケージ | アクター | 開発URL | 担当UC |
|---|---|---|---|
| `packages/guest` | 利用者 | http://localhost:5173 | UC1 予約 / UC4 照会 / UC5 キャンセル |
| `packages/staff` | フロント係 | http://localhost:5174 | UC2 チェックイン / UC3 チェックアウト |
| `packages/api-client` | — | — | 生成した型とHTTPクライアント |
| `packages/ui` | — | — | 両アクター共通の表示部品 |

同一オリジンでパスだけ分けても、cookie・localStorage・CSPは共有されるため認証境界には
なりません。別オリジンで配信することで初めて、フロント係アプリだけをVPNや
リバースプロキシの背後に置けます。詳細と現在の制約は
[`packages/staff/README.md`](packages/staff/README.md) を参照してください。

## 技術構成

- pnpm workspace（`apps/frontend` が root）
- Vite + React + TypeScript
- React Router（データルータ: loader / action）
- Tailwind CSS（UIライブラリは使わず、pure HTML + Tailwind）
- openapi-typescript（`/openapi.json` → TypeScript型を生成）
- openapi-fetch（生成した型で型付けされたHTTPクライアント）

手書きのAPIクライアント型は持たず、`packages/api-client/src/schema.d.ts` を
生成物として扱います。

## 開発

前提: `apps/backend` を起動しておく（`docker compose up --build --wait` で
`http://localhost:8080`）。以下はすべて `apps/frontend` で実行します。

```bash
pnpm install
pnpm gen          # 起動中APIの /openapi.json から型を再生成
pnpm dev:guest    # http://localhost:5173
pnpm dev:staff    # http://localhost:5174
pnpm typecheck    # 全パッケージの型チェック
pnpm build        # 両アプリの型チェック + 本番ビルド
```

APIのベースURLは `VITE_API_BASE_URL`（既定 `http://localhost:8080`）で変更できます。

バックエンドのエンドポイントを変更したら `pnpm gen` で型を再生成してコミットしてください。
CIの `API Schema Drift Check` が、コミットされた `schema.d.ts` とバックエンドの実装が
一致することを検証します。ここが落ちている場合、フロントは存在しないエンドポイントを
叩いており、実行時にはFastAPIの `{"detail":"Not Found"}` が返ります。

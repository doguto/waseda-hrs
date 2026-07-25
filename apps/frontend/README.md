# HRS Frontend

ホテル予約システム（HRS）のデモ用フロントエンドです。`apps/backend` の
FastAPI を叩く SPA で、バックエンドが公開する OpenAPI から型を生成して
型安全に通信します。

## 技術構成

- Vite + React + TypeScript
- React Router（データルータ: loader / action）
- Tailwind CSS（UIライブラリは使わず、pure HTML + Tailwind）
- openapi-typescript（`/openapi.json` → TypeScript 型を生成）
- openapi-fetch（生成した型で型付けされた HTTP クライアント）

手書きのAPIクライアント型は持たず、`src/api/schema.d.ts` を生成物として扱います。

## 画面（UCとの対応）

| 画面 | パス | ユースケース |
|---|---|---|
| 部屋タイプ一覧＋予約照会 | `/` | 閲覧 / UC4 への入口 |
| 部屋タイプ詳細＋予約フォーム | `/rooms/:slug` | UC1 予約登録 |
| 予約詳細＋状態別アクション | `/reservations/:slug` | UC4 照会 / UC2 チェックイン / UC3 チェックアウト / UC5 キャンセル |

予約詳細では予約状態に応じて操作ボタンを出し分けます（RESERVED → チェックイン/
キャンセル、CHECKED_IN → チェックアウト）。

## 開発

前提: `apps/backend` を起動しておく（`docker compose up` で `http://localhost:8080`）。

```bash
pnpm install
pnpm gen      # 起動中APIの /openapi.json から型を再生成
pnpm dev      # http://localhost:5173
pnpm build    # 型チェック + 本番ビルド
```

API のベースURLは `VITE_API_BASE_URL`（既定 `http://localhost:8080`）で変更できます。

バックエンドのエンドポイントを変更したら `pnpm gen` で型を再生成してください。
`GET /room-types` など閲覧APIは backend 側で提供しています。

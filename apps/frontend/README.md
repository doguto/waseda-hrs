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
| 利用者：現在の予約＋部屋タイプ一覧 | `/` | UC1・UC4・UC5への入口 |
| 部屋タイプ詳細＋予約フォーム | `/rooms/:slug` | UC1 予約登録 |
| 予約完了 | `/reservations/:slug/complete` | UC1 予約番号の提示 |
| 利用者：予約詳細 | `/reservations/:slug` | UC4 照会 / UC5 キャンセル |
| フロント係：予約番号検索 | `/front` | UC2・UC3への入口 |
| フロント係：予約処理 | `/front/reservations/:slug` | UC2 チェックイン / UC3 チェックアウト |

予約番号はブラウザに保存され、ホームの「現在の予約」に予約中・宿泊中の予約を
表示します。利用者画面では予約とキャンセル、フロント係画面では予約番号を使った
チェックイン・請求発行・支払い受領・チェックアウトを扱います。請求を発行した
だけではチェックアウトせず、フロント係が利用者からの支払い受領を登録した後に
CHECKED_OUTへ更新します。デモではアカウント認証は行わず、URLと画面を分離して
アクターごとの責務を表現しています。

利用者画面は予約状態を3秒ごと、およびタブへ戻ったときに再取得します。フロント係が
チェックアウトを完了すると、利用者の予約詳細とホームに「ご利用ありがとうございました」
を表示します。

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

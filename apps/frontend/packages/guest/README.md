# HRS Guest (利用者アプリ)

利用者アクターの画面だけを持つSPAです。ワークスペース全体の構成と開発手順は
ワークスペース直下の [`README.md`](../../README.md) を参照してください。

## 画面（UCとの対応）

| 画面 | パス | ユースケース | 09のバウンダリ |
|---|---|---|---|
| 現在の予約＋部屋タイプ一覧 | `/` | UC1・UC4・UC5への入口 | — |
| 部屋タイプ詳細＋予約フォーム | `/rooms/:slug` | UC1 予約登録 | ReservationUI |
| 予約完了 | `/reservations/:slug/complete` | UC1 予約番号の提示 | ReservationUI |
| 予約詳細 | `/reservations/:slug` | UC4 照会 / UC5 キャンセル | InquiryUI / CancellationUI |

チェックイン・チェックアウトはフロント係のユースケース（UC2・UC3）なので、
このアプリには存在しません。`packages/staff` が担当します。

予約番号は `localStorage` に保存され、ホームの「現在の予約」に予約中・宿泊中の
予約を表示します。予約状態は3秒ごと、およびタブへ戻ったときに再取得し、
フロント係がチェックアウトを完了すると「ご利用ありがとうございました」を表示します。

## 開発

```bash
pnpm --filter @hrs/guest dev     # http://localhost:5173
```

APIのベースURLは `VITE_API_BASE_URL`（既定 `http://localhost:8080`）で変更できます。

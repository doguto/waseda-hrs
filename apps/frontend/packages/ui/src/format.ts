import type { ReservationStatus } from "@hrs/api-client";

const yen = new Intl.NumberFormat("ja-JP", {
  style: "currency",
  currency: "JPY",
});

/** 金額(円・整数)を「¥12,345」形式に整形する。 */
export function formatYen(amount: number): string {
  return yen.format(amount);
}

type StatusMeta = { label: string; className: string };

/** 予約状態の日本語ラベルとバッジ配色。 */
export const statusMeta: Record<ReservationStatus, StatusMeta> = {
  RESERVED: { label: "予約済み", className: "bg-blue-100 text-blue-800" },
  CHECKED_IN: { label: "チェックイン済み", className: "bg-green-100 text-green-800" },
  CHECKED_OUT: { label: "チェックアウト済み", className: "bg-gray-200 text-gray-700" },
  CANCELLED: { label: "キャンセル済み", className: "bg-red-100 text-red-800" },
};

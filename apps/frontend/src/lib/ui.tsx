import type { ReactNode } from "react";

import type { ReservationStatus } from "../api/client";
import { statusMeta } from "./format";

/** 予約状態のバッジ。 */
export function StatusBadge({ status }: { status: ReservationStatus }) {
  const meta = statusMeta[status];
  return (
    <span
      className={`inline-block rounded-full px-3 py-1 text-sm font-medium ${meta.className}`}
    >
      {meta.label}
    </span>
  );
}

type AlertTone = "error" | "success" | "info";

const alertTone: Record<AlertTone, string> = {
  error: "border-red-200 bg-red-50 text-red-800",
  success: "border-green-200 bg-green-50 text-green-800",
  info: "border-slate-200 bg-slate-50 text-slate-700",
};

/** 操作結果やエラーの通知。スクリーンリーダー向けに role/aria-live を付与。 */
export function Alert({ tone, children }: { tone: AlertTone; children: ReactNode }) {
  return (
    <p
      role={tone === "error" ? "alert" : "status"}
      aria-live="polite"
      className={`rounded-lg border px-4 py-3 text-sm ${alertTone[tone]}`}
    >
      {children}
    </p>
  );
}

/** ラベル付きのフォーム入力。 */
export function Field({
  label,
  name,
  type = "text",
  required = true,
  defaultValue,
}: {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
  defaultValue?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>
      <input
        name={name}
        type={type}
        required={required}
        defaultValue={defaultValue}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 shadow-sm outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
      />
    </label>
  );
}

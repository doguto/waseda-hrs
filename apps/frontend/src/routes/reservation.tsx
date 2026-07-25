import {
  type ActionFunctionArgs,
  type LoaderFunctionArgs,
  Form,
  useActionData,
  useLoaderData,
  useNavigation,
} from "react-router-dom";

import { type CheckOut, api, errorMessage } from "../api/client";
import { formatYen } from "../lib/format";
import { Alert, StatusBadge } from "../lib/ui";

/** 予約1件を取得する(UC4)。 */
export async function reservationLoader({ params }: LoaderFunctionArgs) {
  const id = params.slug ?? "";
  const { data, error } = await api.GET("/reservations/{reservation_id}", {
    params: { path: { reservation_id: id } },
  });
  if (error || !data) {
    throw new Response("予約が見つかりません", { status: 404 });
  }
  return data;
}

type ActionResult =
  | { error: string }
  | { ok: string }
  | { checkout: CheckOut };

/** 状態遷移の操作(UC2 チェックイン / UC3 チェックアウト / UC5 キャンセル)。 */
export async function reservationAction({
  request,
  params,
}: ActionFunctionArgs): Promise<ActionResult> {
  const id = params.slug ?? "";
  const path = { reservation_id: id };
  const intent = String((await request.formData()).get("intent"));

  if (intent === "check-in") {
    const { error } = await api.POST("/reservations/{reservation_id}/check-in", {
      params: { path },
    });
    return error ? { error: errorMessage(error) } : { ok: "チェックインしました" };
  }
  if (intent === "cancel") {
    const { error } = await api.POST("/reservations/{reservation_id}/cancellation", {
      params: { path },
    });
    return error ? { error: errorMessage(error) } : { ok: "予約をキャンセルしました" };
  }
  if (intent === "check-out") {
    const { data, error } = await api.POST("/reservations/{reservation_id}/check-out", {
      params: { path },
    });
    return error || !data ? { error: errorMessage(error) } : { checkout: data };
  }
  return { error: "不明な操作です" };
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 py-2">
      <dt className="text-slate-500">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}

/** hidden の intent を付けた操作ボタン。 */
function ActionButton({
  intent,
  label,
  variant,
  disabled,
}: {
  intent: string;
  label: string;
  variant: "primary" | "danger";
  disabled: boolean;
}) {
  const styles =
    variant === "danger"
      ? "border border-red-300 text-red-700 hover:bg-red-50"
      : "bg-slate-900 text-white hover:bg-slate-700";
  return (
    <Form method="post">
      <input type="hidden" name="intent" value={intent} />
      <button
        type="submit"
        disabled={disabled}
        className={`rounded-lg px-4 py-2 font-medium disabled:opacity-50 ${styles}`}
      >
        {label}
      </button>
    </Form>
  );
}

export function ReservationPage() {
  const reservation = useLoaderData() as Awaited<ReturnType<typeof reservationLoader>>;
  const actionData = useActionData() as ActionResult | undefined;
  const navigation = useNavigation();
  const busy = navigation.state !== "idle";

  const canCheckIn = reservation.status === "RESERVED";
  const canCancel = reservation.status === "RESERVED";
  const canCheckOut = reservation.status === "CHECKED_IN";

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">予約内容</h1>
          <StatusBadge status={reservation.status} />
        </div>
        <dl className="mt-4 divide-y divide-slate-100">
          <Row label="予約番号" value={reservation.reservation_id} />
          <Row label="宿泊者" value={reservation.guest_name} />
          <Row label="連絡先" value={reservation.guest_contact} />
          <Row
            label="部屋"
            value={`${reservation.room_number}（${reservation.room_type}）`}
          />
          <Row label="チェックイン" value={reservation.check_in_date} />
          <Row label="チェックアウト" value={reservation.check_out_date} />
        </dl>
      </section>

      {actionData && "error" in actionData ? (
        <Alert tone="error">{actionData.error}</Alert>
      ) : null}
      {actionData && "ok" in actionData ? (
        <Alert tone="success">{actionData.ok}</Alert>
      ) : null}
      {actionData && "checkout" in actionData ? (
        <Alert tone="success">
          チェックアウトしました。請求 {formatYen(actionData.checkout.charge.amount)}
          （{actionData.checkout.charge.paid ? "支払い済み" : "未払い"}）。
        </Alert>
      ) : null}

      {canCheckIn || canCancel || canCheckOut ? (
        <section className="flex flex-wrap gap-3">
          {canCheckIn ? (
            <ActionButton
              intent="check-in"
              label="チェックイン"
              variant="primary"
              disabled={busy}
            />
          ) : null}
          {canCheckOut ? (
            <ActionButton
              intent="check-out"
              label="チェックアウト"
              variant="primary"
              disabled={busy}
            />
          ) : null}
          {canCancel ? (
            <ActionButton
              intent="cancel"
              label="キャンセル"
              variant="danger"
              disabled={busy}
            />
          ) : null}
        </section>
      ) : (
        <p className="text-sm text-slate-500">この予約に対して可能な操作はありません。</p>
      )}
    </div>
  );
}

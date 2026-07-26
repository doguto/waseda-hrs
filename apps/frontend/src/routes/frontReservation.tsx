import {
  type ActionFunctionArgs,
  type LoaderFunctionArgs,
  Form,
  Link,
  redirect,
  useActionData,
  useLoaderData,
  useNavigation,
} from "react-router-dom";

import { type Charge, type CheckOut, api, errorMessage } from "../api/client";
import { formatYen } from "../lib/format";
import { DetailRow, ReservationSummary } from "../lib/reservationView";
import { Alert } from "../lib/ui";

export async function frontReservationLoader({ params }: LoaderFunctionArgs) {
  const id = params.slug ?? "";
  const path = { reservation_id: id };
  const [{ data: reservation, error }, { data: charge }] = await Promise.all([
    api.GET("/reservations/{reservation_id}", { params: { path } }),
    api.GET("/reservations/{reservation_id}/charge", { params: { path } }),
  ]);
  if (error || !reservation) {
    throw new Response("予約が見つかりません", { status: 404 });
  }
  return { reservation, charge: charge ?? null };
}

type ActionResult =
  | { error: string }
  | { charge: CheckOut }
  | { payment: CheckOut };

export async function frontReservationAction({
  request,
  params,
}: ActionFunctionArgs): Promise<ActionResult | Response> {
  const id = params.slug ?? "";
  const path = { reservation_id: id };
  const intent = String((await request.formData()).get("intent"));

  if (intent === "check-in") {
    const { error } = await api.POST("/reservations/{reservation_id}/check-in", {
      params: { path },
    });
    return error ? { error: errorMessage(error) } : redirect("/front");
  }
  if (intent === "issue-charge") {
    const { data, error } = await api.POST("/reservations/{reservation_id}/charge", {
      params: { path },
    });
    return error || !data
      ? { error: errorMessage(error) }
      : { charge: data };
  }
  if (intent === "pay") {
    const { data, error } = await api.POST("/reservations/{reservation_id}/payment", {
      params: { path },
    });
    return error || !data
      ? { error: errorMessage(error) }
      : { payment: data };
  }
  return { error: "不明な操作です" };
}

function ActionButton({
  intent,
  label,
  disabled,
}: {
  intent: string;
  label: string;
  disabled: boolean;
}) {
  return (
    <Form method="post">
      <input type="hidden" name="intent" value={intent} />
      <button
        type="submit"
        disabled={disabled}
        className="bg-slate-900 px-4 py-2 font-medium text-white hover:bg-slate-700 disabled:opacity-50"
      >
        {label}
      </button>
    </Form>
  );
}

function PaymentPanel({
  charge,
  nights,
  disabled,
}: {
  charge: Charge;
  nights: number;
  disabled: boolean;
}) {
  return (
    <section className="border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">支払い受領の登録</h2>
          <p className="mt-1 text-sm text-slate-500">
            利用者へ料金を案内し、支払いを受領してから登録します。
          </p>
        </div>
        <span className="shrink-0 border border-amber-200 bg-amber-50 px-3 py-1 text-sm font-medium text-amber-800">
          未払い
        </span>
      </div>

      <dl className="mt-5 divide-y divide-slate-100 border-y border-slate-100">
        <DetailRow label="宿泊日数" value={`${nights} 泊`} />
        <DetailRow label="請求日" value={charge.issued_date} />
        <DetailRow label="請求額" value={formatYen(charge.amount)} />
      </dl>

      <Form method="post" className="mt-5">
        <input type="hidden" name="intent" value="pay" />
        <label className="flex items-start gap-3 text-sm text-slate-700">
          <input
            type="checkbox"
            required
            className="mt-0.5 size-4 accent-slate-900"
          />
          <span>
            利用者から {formatYen(charge.amount)} の支払いを受領しました
          </span>
        </label>
        <button
          type="submit"
          disabled={disabled}
          className="mt-4 w-full bg-slate-900 px-4 py-2.5 font-medium text-white hover:bg-slate-700 disabled:opacity-50"
        >
          支払い受領を登録してチェックアウト
        </button>
      </Form>
    </section>
  );
}

export function FrontReservationPage() {
  const { reservation, charge } = useLoaderData() as Awaited<
    ReturnType<typeof frontReservationLoader>
  >;
  const actionData = useActionData() as ActionResult | undefined;
  const navigation = useNavigation();
  const busy = navigation.state !== "idle";
  const currentCharge =
    actionData && "charge" in actionData ? actionData.charge.charge : charge;
  const nights = Math.max(
    1,
    Math.round(
      (Date.parse(reservation.check_out_date) -
        Date.parse(reservation.check_in_date)) /
        86_400_000,
    ),
  );

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <Link
        to="/front"
        className="inline-block text-sm text-slate-600 hover:text-slate-900"
      >
        ← フロント係画面へ戻る
      </Link>

      <ReservationSummary reservation={reservation} />

      {actionData && "error" in actionData ? (
        <Alert tone="error">{actionData.error}</Alert>
      ) : null}
      {actionData && "charge" in actionData ? (
        <Alert tone="info">
          宿泊料金を計算しました。利用者へ金額を案内してください。
        </Alert>
      ) : null}
      {actionData && "payment" in actionData ? (
        <Alert tone="success">
          {formatYen(actionData.payment.charge.amount)}
          の支払い受領を記録し、チェックアウトが完了しました。
        </Alert>
      ) : null}

      {reservation.status === "RESERVED" ? (
        <section className="border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">チェックイン</h2>
          <p className="mt-1 text-sm text-slate-500">
            予約番号と宿泊内容を確認してから処理します。
          </p>
          <div className="mt-4">
            <ActionButton
              intent="check-in"
              label="チェックイン処理"
              disabled={busy}
            />
          </div>
        </section>
      ) : null}

      {reservation.status === "CHECKED_IN" && !currentCharge ? (
        <section className="border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">チェックアウト</h2>
          <p className="mt-1 text-sm text-slate-500">
            宿泊料金を計算し、利用者へ案内します。
          </p>
          <div className="mt-4">
            <ActionButton
              intent="issue-charge"
              label="宿泊料金を計算する"
              disabled={busy}
            />
          </div>
        </section>
      ) : null}

      {reservation.status === "CHECKED_IN" &&
      currentCharge &&
      !currentCharge.paid ? (
        <PaymentPanel charge={currentCharge} nights={nights} disabled={busy} />
      ) : null}

      {reservation.status === "CHECKED_OUT" &&
      !(actionData && "payment" in actionData) ? (
        <Alert tone="success">支払い済みです。チェックアウトは完了しています。</Alert>
      ) : null}
    </div>
  );
}

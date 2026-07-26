import {
  type ActionFunctionArgs,
  type LoaderFunctionArgs,
  Form,
  redirect,
  useActionData,
  useLoaderData,
  useNavigation,
} from "react-router-dom";

import { api, errorMessage } from "../api/client";
import { formatYen } from "../lib/format";
import { rememberReservation } from "../lib/reservationHistory";
import { Alert, Field } from "../lib/ui";

/** 部屋タイプ1件を取得する(予約フォームの表示用)。 */
export async function roomTypeLoader({ params }: LoaderFunctionArgs) {
  const slug = params.slug ?? "";
  const { data, error } = await api.GET("/room-types/{room_type}", {
    params: { path: { room_type: slug } },
  });
  if (error || !data) {
    throw new Response("部屋タイプが見つかりません", { status: 404 });
  }
  return data;
}

/** 予約フォームの送信 → POST /reservations → 予約詳細へリダイレクト。 */
export async function roomTypeAction({ request, params }: ActionFunctionArgs) {
  const form = await request.formData();
  const { data, error } = await api.POST("/reservations", {
    body: {
      room_type: params.slug ?? "",
      check_in_date: String(form.get("check_in_date")),
      check_out_date: String(form.get("check_out_date")),
      guest_name: String(form.get("guest_name")),
      guest_contact: String(form.get("guest_contact")),
    },
  });
  if (error || !data) {
    return { error: errorMessage(error, "予約に失敗しました") };
  }
  rememberReservation(data.reservation_id);
  return redirect(`/reservations/${data.reservation_id}/complete`);
}

export function RoomTypePage() {
  const room = useLoaderData() as Awaited<ReturnType<typeof roomTypeLoader>>;
  const actionData = useActionData() as { error?: string } | undefined;
  const navigation = useNavigation();
  const submitting = navigation.state === "submitting";
  const soldOut = room.vacant_count <= 0;

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold capitalize">{room.room_type}</h1>
        <p className="mt-1 text-2xl font-bold">
          {formatYen(room.price_per_night)}
          <span className="text-sm font-normal text-slate-500"> / 泊</span>
        </p>
        <p className="mt-1 text-sm text-slate-500">
          {soldOut ? "満室" : `空室 ${room.vacant_count} 室`}
        </p>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">予約する</h2>
        {actionData?.error ? (
          <div className="mt-3">
            <Alert tone="error">{actionData.error}</Alert>
          </div>
        ) : null}
        <Form method="post" className="mt-4 space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="チェックイン日" name="check_in_date" type="date" />
            <Field label="チェックアウト日" name="check_out_date" type="date" />
          </div>
          <Field label="氏名" name="guest_name" />
          <Field label="連絡先" name="guest_contact" />
          <button
            type="submit"
            disabled={soldOut || submitting}
            className="w-full rounded-lg bg-slate-900 px-4 py-2.5 font-medium text-white hover:bg-slate-700 disabled:bg-slate-300"
          >
            {submitting ? "送信中..." : "この内容で予約する"}
          </button>
        </Form>
      </section>
    </div>
  );
}

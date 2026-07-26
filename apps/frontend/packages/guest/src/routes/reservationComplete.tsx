import { type LoaderFunctionArgs, Link, useLoaderData } from "react-router-dom";

import { api } from "../api";
import { StatusBadge } from "@hrs/ui";

export async function reservationCompleteLoader({ params }: LoaderFunctionArgs) {
  const id = params.slug ?? "";
  const { data, error } = await api.GET("/reservations/{reservation_id}", {
    params: { path: { reservation_id: id } },
  });
  if (error || !data) {
    throw new Response("予約が見つかりません", { status: 404 });
  }
  return data;
}

export function ReservationCompletePage() {
  const reservation = useLoaderData() as Awaited<
    ReturnType<typeof reservationCompleteLoader>
  >;

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <section className="border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-green-700">予約を受け付けました</p>
            <h1 className="mt-1 text-2xl font-bold">予約完了</h1>
          </div>
          <StatusBadge status={reservation.status} />
        </div>

        <dl className="mt-6 space-y-3 border-y border-slate-100 py-4">
          <div>
            <dt className="text-sm text-slate-500">予約番号</dt>
            <dd className="mt-1 break-all font-mono text-sm font-semibold">
              {reservation.reservation_id}
            </dd>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-slate-500">宿泊日</dt>
              <dd className="font-medium">
                {reservation.check_in_date} - {reservation.check_out_date}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-slate-500">客室</dt>
              <dd className="font-medium">
                {reservation.room_number}（{reservation.room_type}）
              </dd>
            </div>
          </div>
        </dl>

        <p className="mt-4 text-sm text-slate-600">
          この予約はホームの「現在の予約」から確認できます。
        </p>
        <Link
          to="/"
          className="mt-6 block bg-slate-900 px-4 py-2.5 text-center font-medium text-white hover:bg-slate-700"
        >
          ホームへ戻る
        </Link>
      </section>
    </div>
  );
}

import { type FormEvent } from "react";
import { Link, useLoaderData, useNavigate } from "react-router-dom";

import type { Reservation } from "@hrs/api-client";
import { api } from "../api";
import { formatYen } from "@hrs/ui";
import {
  forgetReservations,
  getReservationIds,
  rememberReservation,
} from "../lib/reservationHistory";
import { StatusBadge } from "@hrs/ui";
import { useAutoRevalidate } from "../lib/useAutoRevalidate";

const ACTIVE_STATUSES = new Set(["RESERVED", "CHECKED_IN"]);

/** トップページ: 部屋タイプと、このブラウザで扱った予約を取得する。 */
export async function homeLoader() {
  const { data: roomTypes, error } = await api.GET("/room-types");
  if (error || !roomTypes) {
    throw new Response("部屋タイプの取得に失敗しました", { status: 502 });
  }

  const reservationIds = getReservationIds();
  const results = await Promise.all(
    reservationIds.map(async (reservationId) => {
      const { data } = await api.GET("/reservations/{reservation_id}", {
        params: { path: { reservation_id: reservationId } },
      });
      return data;
    }),
  );
  const missingIds = reservationIds.filter((_, index) => !results[index]);
  if (missingIds.length > 0) forgetReservations(missingIds);

  const reservations = results.filter(
    (reservation): reservation is Reservation =>
      Boolean(reservation),
  );
  return {
    roomTypes,
    activeReservations: reservations.filter((reservation) =>
      ACTIVE_STATUSES.has(reservation.status),
    ),
    completedReservations: reservations.filter(
      (reservation) => reservation.status === "CHECKED_OUT",
    ),
  };
}

/** 予約番号から予約詳細へ移動する照会ボックス。 */
function LookupForm() {
  const navigate = useNavigate();
  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const id = new FormData(event.currentTarget).get("id");
    const trimmed = String(id ?? "").trim();
    if (trimmed) {
      rememberReservation(trimmed);
      navigate(`/reservations/${trimmed}`);
    }
  };
  return (
    <form
      onSubmit={onSubmit}
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <h2 className="text-base font-semibold">予約番号で照会</h2>
      <p className="mt-1 text-sm text-slate-500">
        予約後に発行された予約番号を入力してください。
      </p>
      <div className="mt-3 flex gap-2">
        <input
          name="id"
          aria-label="予約番号"
          placeholder="例: 51aebfb3-9c8d-..."
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 shadow-sm outline-none focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
        />
        <button
          type="submit"
          className="rounded-lg bg-slate-900 px-4 py-2 font-medium text-white hover:bg-slate-700"
        >
          照会
        </button>
      </div>
    </form>
  );
}

export function HomePage() {
  const { roomTypes, activeReservations, completedReservations } =
    useLoaderData() as Awaited<ReturnType<typeof homeLoader>>;
  useAutoRevalidate();
  const latestCompleted = completedReservations[0];

  return (
    <div className="space-y-8">
      {latestCompleted ? (
        <section
          aria-live="polite"
          className="border border-green-200 bg-green-50 px-5 py-4 text-green-900"
        >
          <h1 className="text-xl font-bold">ご利用ありがとうございました</h1>
          <p className="mt-1 text-sm">
            {latestCompleted.room_number}号室のチェックアウトが完了しました。
          </p>
        </section>
      ) : null}

      <section>
        <h1 className="text-2xl font-bold">現在の予約</h1>
        {activeReservations.length > 0 ? (
          <ul className="mt-4 divide-y divide-slate-100 border border-slate-200 bg-white shadow-sm">
            {activeReservations.map((reservation) => (
              <li key={reservation.reservation_id}>
                <Link
                  to={`/reservations/${reservation.reservation_id}`}
                  className="flex items-center justify-between gap-4 p-4 hover:bg-slate-50"
                >
                  <div className="min-w-0">
                    <p className="font-semibold">
                      {reservation.check_in_date} - {reservation.check_out_date}
                    </p>
                    <p className="mt-1 text-sm text-slate-500">
                      {reservation.room_number}（{reservation.room_type}）・
                      {reservation.guest_name}
                    </p>
                  </div>
                  <StatusBadge status={reservation.status} />
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 border border-dashed border-slate-300 bg-white px-4 py-5 text-sm text-slate-500">
            予約中または宿泊中の予約はありません。
          </p>
        )}
      </section>

      <section id="rooms" className="scroll-mt-6">
        <h2 className="text-xl font-bold">部屋を選ぶ</h2>
        <p className="mt-1 text-slate-600">
          お好みの部屋タイプを選んで予約に進んでください。
        </p>
        <ul className="mt-5 grid gap-4 sm:grid-cols-2">
          {roomTypes.map((room) => {
            const soldOut = room.vacant_count <= 0;
            return (
              <li key={room.room_type}>
                <article className="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <h2 className="text-lg font-semibold capitalize">
                    {room.room_type}
                  </h2>
                  <p className="mt-1 text-2xl font-bold">
                    {formatYen(room.price_per_night)}
                    <span className="text-sm font-normal text-slate-500"> / 泊</span>
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    {soldOut ? "満室" : `空室 ${room.vacant_count} 室`}
                  </p>
                  <Link
                    to={`/rooms/${room.room_type}`}
                    aria-disabled={soldOut}
                    className={`mt-4 inline-block rounded-lg px-4 py-2 text-center font-medium ${
                      soldOut
                        ? "pointer-events-none bg-slate-100 text-slate-400"
                        : "bg-slate-900 text-white hover:bg-slate-700"
                    }`}
                  >
                    {soldOut ? "満室" : "予約する"}
                  </Link>
                </article>
              </li>
            );
          })}
        </ul>
      </section>
      <LookupForm />
    </div>
  );
}

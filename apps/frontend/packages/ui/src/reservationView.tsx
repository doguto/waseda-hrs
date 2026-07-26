import type { Reservation } from "@hrs/api-client";
import { StatusBadge } from "./ui";

export function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 py-2">
      <dt className="shrink-0 text-slate-500">{label}</dt>
      <dd className="min-w-0 break-words text-right font-medium">{value}</dd>
    </div>
  );
}

export function ReservationSummary({
  reservation,
}: {
  reservation: Reservation;
}) {
  return (
    <section className="border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-xl font-bold">予約内容</h1>
        <StatusBadge status={reservation.status} />
      </div>
      <dl className="mt-4 divide-y divide-slate-100">
        <DetailRow label="予約番号" value={reservation.reservation_id} />
        <DetailRow label="宿泊者" value={reservation.guest_name} />
        <DetailRow label="連絡先" value={reservation.guest_contact} />
        <DetailRow
          label="客室"
          value={`${reservation.room_number}（${reservation.room_type}）`}
        />
        <DetailRow label="チェックイン" value={reservation.check_in_date} />
        <DetailRow label="チェックアウト" value={reservation.check_out_date} />
      </dl>
    </section>
  );
}

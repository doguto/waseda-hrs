import { useState } from "react";
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

import { errorMessage } from "@hrs/api-client";
import { api } from "../api";
import { ReservationSummary } from "@hrs/ui";
import { Alert } from "@hrs/ui";
import { useAutoRevalidate } from "../lib/useAutoRevalidate";

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

export async function reservationAction({
  request,
  params,
}: ActionFunctionArgs): Promise<{ error: string } | Response> {
  const intent = String((await request.formData()).get("intent"));
  if (intent !== "cancel") return { error: "不明な操作です" };

  const id = params.slug ?? "";
  const { error } = await api.POST("/reservations/{reservation_id}/cancellation", {
    params: { path: { reservation_id: id } },
  });
  return error ? { error: errorMessage(error) } : redirect("/");
}

export function ReservationPage() {
  const reservation = useLoaderData() as Awaited<
    ReturnType<typeof reservationLoader>
  >;
  const actionData = useActionData() as { error?: string } | undefined;
  const busy = useNavigation().state !== "idle";
  // UC5 手順5・6: キャンセルの指示と確定を分ける。確定するまで予約は変更しない。
  const [confirming, setConfirming] = useState(false);
  useAutoRevalidate();

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <Link to="/" className="inline-block text-sm text-slate-600 hover:text-slate-900">
        ← 利用者画面へ戻る
      </Link>

      <ReservationSummary reservation={reservation} />

      {actionData?.error ? <Alert tone="error">{actionData.error}</Alert> : null}

      {reservation.status === "RESERVED" ? (
        <section className="border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">予約の管理</h2>
          <p className="mt-1 text-sm text-slate-500">
            この予約を取り消す場合のみキャンセルしてください。
          </p>

          {confirming ? (
            <div aria-live="polite" className="mt-4 border border-red-200 bg-red-50 p-4">
              <p className="font-medium text-red-900">
                この予約をキャンセルします。よろしいですか？
              </p>
              <p className="mt-1 text-sm text-red-800">
                キャンセルすると元に戻せません。客室は空室に戻ります。
              </p>
              <div className="mt-4 flex gap-3">
                <Form method="post">
                  <input type="hidden" name="intent" value="cancel" />
                  <button
                    type="submit"
                    disabled={busy}
                    className="bg-red-700 px-4 py-2 font-medium text-white hover:bg-red-800 disabled:opacity-50"
                  >
                    キャンセルを確定する
                  </button>
                </Form>
                {/* 代替フロー6a: 確定せずに戻る。予約は「予約済み」のまま維持される。 */}
                <button
                  type="button"
                  onClick={() => setConfirming(false)}
                  disabled={busy}
                  className="border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                >
                  取りやめる
                </button>
              </div>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setConfirming(true)}
              className="mt-4 border border-red-300 px-4 py-2 font-medium text-red-700 hover:bg-red-50"
            >
              予約をキャンセル
            </button>
          )}
        </section>
      ) : null}

      {reservation.status === "CHECKED_IN" ? (
        <Alert tone="info">
          チェックイン済みです。チェックアウト処理はホテルのフロントで行います。
        </Alert>
      ) : null}

      {reservation.status === "CHECKED_OUT" ? (
        <section
          aria-live="polite"
          className="border border-green-200 bg-green-50 px-5 py-4 text-green-900"
        >
          <h2 className="text-xl font-bold">ご利用ありがとうございました</h2>
          <p className="mt-1 text-sm">
            お支払いとチェックアウトの手続きが完了しました。
          </p>
        </section>
      ) : null}
    </div>
  );
}

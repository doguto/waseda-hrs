import createClient from "openapi-fetch";

import type { components, paths } from "./schema";

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080";

/** OpenAPIスキーマから型付けされたHTTPクライアント。 */
export const api = createClient<paths>({ baseUrl });

export type RoomType = components["schemas"]["RoomTypeResponse"];
export type Reservation = components["schemas"]["ReservationResponse"];
export type Charge = components["schemas"]["ChargeResponse"];
export type CheckOut = components["schemas"]["CheckOutResponse"];
export type ReservationStatus = components["schemas"]["ReservationStatus"];

/** FastAPIのエラーレスポンス(HTTPException/バリデーション)から表示用メッセージを取り出す。 */
export function errorMessage(error: unknown, fallback = "エラーが発生しました"): string {
  if (error && typeof error === "object" && "detail" in error) {
    const detail = (error as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return "入力内容を確認してください";
  }
  return fallback;
}

import createClient from "openapi-fetch";

import type { components, paths } from "./schema";

/** OpenAPIスキーマから型付けされたHTTPクライアントを作る。
接続先は各アプリが渡す。利用者アプリとフロント係アプリは別オリジンで配信し、
それぞれ別のゲートウェイを向きうるため、この共有パッケージは接続先を持たない。 */
export function createApiClient(baseUrl: string) {
  return createClient<paths>({ baseUrl });
}

export type ApiClient = ReturnType<typeof createApiClient>;

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

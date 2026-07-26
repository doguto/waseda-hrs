/** 利用者アプリ・フロント係アプリの両方が使う表示部品。
どちらのアクターにも属さないもの(整形・状態バッジ・通知・予約内容の表示)だけを置く。
アクター固有の画面は各アプリの routes/ に置く。 */

export { formatYen, statusMeta } from "./format";
export { Alert, Field, StatusBadge } from "./ui";
export { DetailRow, ReservationSummary } from "./reservationView";

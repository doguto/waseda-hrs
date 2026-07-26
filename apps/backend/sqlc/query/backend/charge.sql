-- 宿泊料金を未払いの請求として発行する(UC3 料金を計算・提示する)。
-- 同じ予約への再実行では既存の請求を返し、金額を上書きしない。
-- name: CreateCharge :one
INSERT INTO charges (reservation_id, amount, issued_date, paid)
VALUES ($1, $2, $3, FALSE)
ON CONFLICT (reservation_id) DO UPDATE
SET reservation_id = EXCLUDED.reservation_id
RETURNING id, reservation_id, amount, issued_date, paid;

-- 予約番号に対応する請求を取得する。
-- name: GetChargeByReservationId :one
SELECT id, reservation_id, amount, issued_date, paid
FROM charges
WHERE reservation_id = $1;

-- 支払いとチェックアウトを同一トランザクションで処理するため、請求をロックする。
-- name: LockChargeByReservationId :one
SELECT id, reservation_id, amount, issued_date, paid
FROM charges
WHERE reservation_id = $1
FOR UPDATE;

-- 利用者からの支払いを受領した後、請求を支払い済みに更新する。
-- name: MarkChargePaid :one
UPDATE charges
SET paid = TRUE
WHERE reservation_id = $1
RETURNING id, reservation_id, amount, issued_date, paid;

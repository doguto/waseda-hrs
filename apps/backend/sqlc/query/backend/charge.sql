-- 請求を発行し支払い済みとして記録する(UC3 支払いを記録する)。
-- 予約1件につき1つ(charges.reservation_id は UNIQUE)。
-- name: CreatePaidCharge :one
INSERT INTO charges (reservation_id, amount, issued_date, paid)
VALUES ($1, $2, $3, TRUE)
RETURNING id;

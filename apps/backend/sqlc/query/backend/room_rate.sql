-- 客室タイプの1泊単価を取得する(UC3 チェックアウトの料金計算)。
-- name: GetRoomRate :one
SELECT room_type, price_per_night
FROM room_rates
WHERE room_type = $1;

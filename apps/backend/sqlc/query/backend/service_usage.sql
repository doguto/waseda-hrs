-- 予約に紐づく追加サービス利用を列挙する(UC3 料金計算)。
-- name: ListServiceUsages :many
SELECT service_name, fee
FROM service_usages
WHERE reservation_id = $1
ORDER BY service_name;

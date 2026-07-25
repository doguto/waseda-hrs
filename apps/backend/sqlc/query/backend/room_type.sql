-- 部屋タイプ一覧を単価と空室数つきで返す(フロントの閲覧画面用)。
-- vacant_count は当該タイプの VACANT な客室数。::int で bigint を int に落とす。
-- name: ListRoomTypes :many
SELECT
    rr.room_type,
    rr.price_per_night,
    COUNT(rm.room_number) FILTER (WHERE rm.status = 'VACANT')::int AS vacant_count
FROM room_rates AS rr
LEFT JOIN rooms AS rm ON rm.room_type = rr.room_type
GROUP BY rr.room_type, rr.price_per_night
ORDER BY rr.room_type;

-- 部屋タイプ1件を単価と空室数つきで返す(部屋詳細/予約フォーム用)。
-- name: GetRoomType :one
SELECT
    rr.room_type,
    rr.price_per_night,
    COUNT(rm.room_number) FILTER (WHERE rm.status = 'VACANT')::int AS vacant_count
FROM room_rates AS rr
LEFT JOIN rooms AS rm ON rm.room_type = rr.room_type
WHERE rr.room_type = $1
GROUP BY rr.room_type, rr.price_per_night;

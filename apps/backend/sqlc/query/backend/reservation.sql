-- 予約番号(id)から予約内容を1件取得する。
-- UC4 の InquiryControl.予約を検索する(予約番号) に対応。
-- 予約内容には利用者の氏名・連絡先と客室情報を含めるため guests / rooms を結合する。
-- name: GetReservationById :one
SELECT
    r.id,
    r.check_in_date,
    r.check_out_date,
    r.status,
    g.name AS guest_name,
    g.contact AS guest_contact,
    rm.room_number,
    rm.room_type
FROM reservations AS r
INNER JOIN guests AS g ON g.id = r.guest_id
INNER JOIN rooms AS rm ON rm.room_number = r.room_number
WHERE r.id = $1;

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

-- 予約と客室の行をロックしたうえで予約内容を取得する。
-- UC5 のように状態を書き換える前提の読み取りで使う。GetReservationById との違いは
-- FOR UPDATE OF r, rm のみ(guests は変更しないのでロック対象に含めない)。
-- reservation と room を単一クエリで固定順にロックし、並行遷移を直列化する。
-- name: LockReservationDetailById :one
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
WHERE r.id = $1
FOR UPDATE OF r, rm;

-- 予約の状態を更新する。事前条件(遷移の可否)はドメイン側で検査済みである前提。
-- name: SetReservationStatus :exec
UPDATE reservations
SET status = $2
WHERE id = $1;

-- 予約を登録する(UC1 予約登録)。status は schema の DEFAULT 'RESERVED' に任せる。
-- name: CreateReservation :one
INSERT INTO reservations (guest_id, room_number, check_in_date, check_out_date)
VALUES ($1, $2, $3, $4)
RETURNING id;

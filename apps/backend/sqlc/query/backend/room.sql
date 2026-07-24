-- 客室の状態を更新する。呼び出し側で LockReservationDetailById により
-- 当該 room 行をロック済みである前提。
-- name: SetRoomStatus :exec
UPDATE rooms
SET status = $2
WHERE room_number = $1;

-- 指定タイプの空室を1つ選び、その行をロックして返す(UC1 予約登録)。
-- SKIP LOCKED により、同時に予約しようとする他トランザクションは別の空室を掴む
-- (同じ部屋のダブルブッキングを避けつつ、待たずにスループットを保つ)。
-- 空室が無ければ行を返さない。
-- name: FindAndLockVacantRoom :one
SELECT room_number, room_type
FROM rooms
WHERE room_type = $1
  AND status = 'VACANT'
ORDER BY room_number
FOR UPDATE SKIP LOCKED
LIMIT 1;

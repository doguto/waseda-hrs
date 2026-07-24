-- 客室の状態を更新する。呼び出し側で LockReservationDetailById により
-- 当該 room 行をロック済みである前提。
-- name: SetRoomStatus :exec
UPDATE rooms
SET status = $2
WHERE room_number = $1;

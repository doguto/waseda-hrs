-- 予約時に利用者の氏名・連絡先を登録する(UC1 予約登録)。
-- name: CreateGuest :one
INSERT INTO guests (name, contact)
VALUES ($1, $2)
RETURNING id;

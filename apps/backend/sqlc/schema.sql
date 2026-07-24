-- HRS DB schema (declarative source of truth).
-- sqldef がこのファイルとDBの差分を適用し、sqlc がこのファイルを型情報の基にする。
-- 分析工程のクラス図(docs/uml/09)のエンティティを実装用に写したもの。
-- 現状は UC4「予約内容を確認する」の縦切りに必要な範囲のみを定義し、
-- 残りのエンティティ(RoomRate / ServiceUsage / Charge)は後続UCで追加する。

-- 客室の状態(09の RoomStatus)。
CREATE TYPE room_status AS ENUM ('VACANT', 'RESERVED', 'OCCUPIED');

-- 予約の状態(09の ReservationStatus)。
CREATE TYPE reservation_status AS ENUM (
    'RESERVED',
    'CHECKED_IN',
    'CHECKED_OUT',
    'CANCELLED'
);

-- 利用者の記録(09の Guest)。予約時に氏名・連絡先を登録する。
CREATE TABLE guests (
    id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name    text NOT NULL,
    contact text NOT NULL
);

-- 客室(09の Room)。room_number を人が扱う識別子としてそのままキーにする。
CREATE TABLE rooms (
    room_number text        PRIMARY KEY,
    room_type   text        NOT NULL,
    status      room_status NOT NULL DEFAULT 'VACANT'
);

-- 予約(09の Reservation)。id が利用者に伝える予約番号を兼ねる。
CREATE TABLE reservations (
    id             uuid               PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_id       uuid               NOT NULL REFERENCES guests (id),
    room_number    text               NOT NULL REFERENCES rooms (room_number),
    check_in_date  date               NOT NULL,
    check_out_date date               NOT NULL,
    status         reservation_status NOT NULL DEFAULT 'RESERVED'
);

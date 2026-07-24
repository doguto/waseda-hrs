-- HRS DB schema (declarative source of truth).
-- sqldef がこのファイルとDBの差分を適用し、sqlc がこのファイルを型情報の基にする。
-- 分析工程のクラス図(docs/uml/09)のエンティティを実装用に写したもの。
-- 金額は円(整数)で保持する(JPY は最小単位が円で小数を持たないため)。

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

-- 料金表(09の RoomRate)。客室タイプごとの1泊単価を保持する。
CREATE TABLE room_rates (
    room_type       text    PRIMARY KEY,
    price_per_night integer NOT NULL
);

-- 追加サービス利用(09の ServiceUsage)。予約ごとの追加料金。
CREATE TABLE service_usages (
    id             uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id uuid    NOT NULL REFERENCES reservations (id),
    service_name   text    NOT NULL,
    fee            integer NOT NULL
);

-- 請求(09の Charge)。予約1件につき1つ。チェックアウト時に発行・支払い記録する。
CREATE TABLE charges (
    id             uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id uuid    NOT NULL UNIQUE REFERENCES reservations (id),
    amount         integer NOT NULL,
    issued_date    date    NOT NULL,
    paid           boolean NOT NULL DEFAULT false
);

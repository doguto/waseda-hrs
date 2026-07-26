-- Demo data for local Docker Compose environments.
-- This file runs only when PostgreSQL creates a new data volume.

INSERT INTO room_rates (room_type, price_per_night)
VALUES
    ('standard', 10000),
    ('deluxe', 16000),
    ('suite', 25000)
ON CONFLICT (room_type) DO UPDATE
SET price_per_night = EXCLUDED.price_per_night;

INSERT INTO rooms (room_number, room_type, status)
VALUES
    ('101', 'standard', 'VACANT'),
    ('102', 'standard', 'VACANT'),
    ('103', 'standard', 'VACANT'),
    ('201', 'deluxe', 'VACANT'),
    ('202', 'deluxe', 'VACANT'),
    ('301', 'suite', 'VACANT')
ON CONFLICT (room_number) DO NOTHING;

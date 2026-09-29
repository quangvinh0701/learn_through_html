-- =============================================================
-- Lab 11 CDC — init/01-init.sql
-- Chạy TỰ ĐỘNG 1 lần khi Postgres khởi tạo volume lần đầu
--   (mount vào /docker-entrypoint-initdb.d).
-- Trích & chuyển thể từ 11-streaming-data-api-masterclass.html
--   (Module 13 Lab, block "init.sql"). Đã bổ sung seed vài chục dòng.
-- =============================================================

-- ── Bảng orders (CDC sẽ capture bảng này) ──
CREATE TABLE IF NOT EXISTS orders (
    order_id    TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    total       DECIMAL(12, 2) NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Bảng order_items (đi kèm, nằm trong table.include.list của connector) ──
CREATE TABLE IF NOT EXISTS order_items (
    item_id    BIGSERIAL PRIMARY KEY,
    order_id   TEXT NOT NULL REFERENCES orders(order_id),
    sku        TEXT NOT NULL,
    qty        INT  NOT NULL CHECK (qty > 0),
    unit_price DECIMAL(12, 2) NOT NULL
);

-- ── (Tùy chọn) user riêng cho Debezium ──
-- Lab dùng thẳng superuser 'postgres' cho gọn. Trên production nên tách user
-- có quyền REPLICATION như dưới đây (đang comment để tránh phải grant thủ công):
-- CREATE USER debezium WITH REPLICATION PASSWORD 'debezium';
-- GRANT CONNECT ON DATABASE labdb TO debezium;
-- GRANT USAGE ON SCHEMA public TO debezium;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium;

-- ── Seed: vài chục dòng orders ──
-- 6 dòng "đẹp" cố định để dễ test UPDATE/DELETE theo order_id...
INSERT INTO orders (order_id, customer_id, total, status) VALUES
    ('ORD-0001', 'CUST-A', 299000,  'pending'),
    ('ORD-0002', 'CUST-B', 599000,  'shipped'),
    ('ORD-0003', 'CUST-C', 1299000, 'delivered'),
    ('ORD-0004', 'CUST-A', 89000,   'pending'),
    ('ORD-0005', 'CUST-D', 450000,  'cancelled'),
    ('ORD-0006', 'CUST-E', 720000,  'shipped')
ON CONFLICT (order_id) DO NOTHING;

-- ...cộng thêm ~36 dòng sinh tự động cho "đủ vài chục".
INSERT INTO orders (order_id, customer_id, total, status, created_at)
SELECT
    'ORD-' || LPAD((g + 100)::text, 4, '0'),
    'CUST-' || chr(65 + (g % 5)),                       -- CUST-A..CUST-E
    (50000 + (g * 12345) % 1500000)::numeric(12,2),     -- tổng tiền giả
    (ARRAY['pending','shipped','delivered','cancelled'])[1 + (g % 4)],
    NOW() - (g || ' hours')::interval
FROM generate_series(1, 36) AS g
ON CONFLICT (order_id) DO NOTHING;

-- Vài dòng order_items khớp order_id có thật
INSERT INTO order_items (order_id, sku, qty, unit_price)
SELECT
    'ORD-000' || (1 + (g % 6)),
    'SKU-' || LPAD(g::text, 3, '0'),
    1 + (g % 4),
    (10000 + (g * 5000) % 300000)::numeric(12,2)
FROM generate_series(1, 18) AS g;

-- ── ⭐ REPLICA IDENTITY FULL ──
-- Bắt buộc để event UPDATE/DELETE mang theo GIÁ TRỊ CŨ đầy đủ (before image).
-- Mặc định Postgres chỉ log primary key ở "before" -> consumer không thấy cột cũ.
ALTER TABLE orders      REPLICA IDENTITY FULL;
ALTER TABLE order_items REPLICA IDENTITY FULL;

-- =============================================================
-- Lab 27 — init/cassandra-schema.cql
-- Cassandra KHONG co co che tu chay script luc khoi tao (khac Postgres,
-- khac Mongo). Chay bang tay SAU khi container healthy:
--
--   docker exec nosql-cassandra cqlsh -f /schema/cassandra-schema.cql
--
-- Trich & chuyen the tu 27-nosql-distributed-storage-masterclass.html
--   (Chuong 8 — wide-column, Chuong 12 — bucketing chuoi thoi gian,
--    Chuong 16 — lab buoc 5).
-- =============================================================

-- ── Keyspace ────────────────────────────────────────────────
-- SimpleStrategy + RF=1 vi lab chi co MOT node. Day cung la gioi han lon
-- nhat cua lab: RF=1 thi khong co gi de hoc ve quorum. Muon hoc quorum that,
-- nhan cluster len 3 node (README, Bai tap 5) roi doi sang:
--   NetworkTopologyStrategy voi 'dc1': 3, va doc/ghi bang QUORUM.
DROP KEYSPACE IF EXISTS shop;

CREATE KEYSPACE shop
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE shop;

-- ── Bang 1: don hang theo khach, moi nhat truoc ─────────────
-- Access pattern: "liet ke don cua khach X, moi nhat truoc, phan trang".
-- Khoa phan vung = customer_id  -> moi khach mot phan vung.
-- Khoa gom (clustering) = created_at DESC, order_id  -> sap san tren dia,
--   doc khong can sort. order_id lam duoi de tranh dung created_at trung.
CREATE TABLE orders_by_customer (
    customer_id  text,
    created_at   timestamp,
    order_id     text,
    total        decimal,
    status       text,
    PRIMARY KEY ((customer_id), created_at, order_id)
) WITH CLUSTERING ORDER BY (created_at DESC, order_id ASC)
  AND comment = 'AP-6: don cua mot khach, moi nhat truoc';

-- ── Bang 2: cung du lieu, khoa khac — vi query khac ─────────
-- Access pattern: "lay chi tiet don theo order_id".
-- Trong Cassandra, mot cau hoi moi = mot bang moi. Day KHONG phai lang phi,
-- day la danh doi: ghi nhieu lan de doc mot lan (Chuong 8).
CREATE TABLE orders_by_id (
    order_id     text PRIMARY KEY,
    customer_id  text,
    created_at   timestamp,
    total        decimal,
    status       text,
    items        list<frozen<map<text, text>>>
) WITH comment = 'AP-5: chi tiet mot don theo order_id';

-- ── Bang 3: chuoi thoi gian CO BUCKETING ────────────────────
-- Access pattern: "doc su kien cua thiet bi X trong khoang thoi gian".
-- Khoa phan vung GOM CA bucket ngay. Neu chi lay device_id lam khoa phan
-- vung, phan vung se lon vo han theo thoi gian — anti-pattern "partition
-- tang khong chan" (Chuong 12, muc 3).
--   1 thiet bi x 1 su kien/giay x 1 ngay = 86.400 dong/phan vung.
--   Nguong an toan thuc te: < 100 MB va < 100.000 dong moi phan vung.
-- default_time_to_live = 30 ngay: dong tu bien mat, khong can job xoa.
CREATE TABLE events_by_device (
    device_id   text,
    day         date,
    ts          timestamp,
    event_type  text,
    payload     text,
    PRIMARY KEY ((device_id, day), ts)
) WITH CLUSTERING ORDER BY (ts DESC)
  AND default_time_to_live = 2592000
  AND gc_grace_seconds = 864000
  AND compaction = {'class': 'TimeWindowCompactionStrategy',
                    'compaction_window_unit': 'DAYS',
                    'compaction_window_size': 1}
  AND comment = 'Chuoi thoi gian: bucket theo ngay + TTL 30 ngay + TWCS';

-- ── Bang 4: TONG HOP TRUOC (pre-aggregation) bang counter ───
-- Doc mot dong thay vi quet 86.400 dong. Counter KHONG idempotent:
-- retry mot lan UPDATE la cong hai lan. Chi dung khi sai lech nho chap nhan duoc.
CREATE TABLE event_counts_by_day (
    device_id  text,
    day        date,
    event_type text,
    n          counter,
    PRIMARY KEY ((device_id, day), event_type)
) WITH comment = 'Tong hop truoc — doc 1 dong thay vi quet ca phan vung';

-- ── Bang 5: THIET KE SAI CO CHU DICH ────────────────────────
-- Khoa phan vung don dieu: MOI su kien trong ngay vao DUNG MOT phan vung,
-- tuc mot node (va cac ban sao cua no) chiu 100% luong ghi.
-- Bai tap 3 trong README: do do lech va sua lai.
CREATE TABLE events_by_day_bad (
    day         date,
    ts          timestamp,
    device_id   text,
    event_type  text,
    PRIMARY KEY ((day), ts, device_id)
) WITH comment = 'CO Y SAI: khoa phan vung don dieu -> hot partition';

-- ── Du lieu mau ─────────────────────────────────────────────
INSERT INTO orders_by_customer (customer_id, created_at, order_id, total, status)
VALUES ('C-01', '2026-07-28 09:00:00+0000', 'O-1001', 448000, 'delivered');
INSERT INTO orders_by_customer (customer_id, created_at, order_id, total, status)
VALUES ('C-01', '2026-07-29 14:20:00+0000', 'O-1002', 890000, 'shipped');
INSERT INTO orders_by_customer (customer_id, created_at, order_id, total, status)
VALUES ('C-01', '2026-07-30 08:10:00+0000', 'O-1004', 275000, 'pending');
INSERT INTO orders_by_customer (customer_id, created_at, order_id, total, status)
VALUES ('C-02', '2026-07-29 15:05:00+0000', 'O-1003', 1590000, 'pending');
INSERT INTO orders_by_customer (customer_id, created_at, order_id, total, status)
VALUES ('C-03', '2026-07-30 08:45:00+0000', 'O-1005', 6200000, 'pending');

INSERT INTO orders_by_id (order_id, customer_id, created_at, total, status, items)
VALUES ('O-1001', 'C-01', '2026-07-28 09:00:00+0000', 448000, 'delivered',
        [{'sku': 'SKU-A', 'qty': '2'}, {'sku': 'SKU-C', 'qty': '1'}]);

INSERT INTO events_by_device (device_id, day, ts, event_type, payload)
VALUES ('DEV-01', '2026-07-30', '2026-07-30 08:00:00+0000', 'heartbeat', '{"t":36}');
INSERT INTO events_by_device (device_id, day, ts, event_type, payload)
VALUES ('DEV-01', '2026-07-30', '2026-07-30 08:00:30+0000', 'heartbeat', '{"t":37}');
INSERT INTO events_by_device (device_id, day, ts, event_type, payload)
VALUES ('DEV-02', '2026-07-30', '2026-07-30 08:00:05+0000', 'alarm', '{"code":"E12"}');

UPDATE event_counts_by_day SET n = n + 2
  WHERE device_id = 'DEV-01' AND day = '2026-07-30' AND event_type = 'heartbeat';
UPDATE event_counts_by_day SET n = n + 1
  WHERE device_id = 'DEV-02' AND day = '2026-07-30' AND event_type = 'alarm';

-- ── Kiem chung ──────────────────────────────────────────────
-- Chay duoc (khoa phan vung nam trong WHERE):
SELECT order_id, created_at, total, status FROM orders_by_customer
  WHERE customer_id = 'C-01';

SELECT ts, event_type FROM events_by_device
  WHERE device_id = 'DEV-01' AND day = '2026-07-30'
    AND ts >= '2026-07-30 00:00:00+0000';

SELECT * FROM event_counts_by_day WHERE device_id = 'DEV-01' AND day = '2026-07-30';

-- Cau duoi day SE BAO LOI — do la muc dich:
--   InvalidRequest: ... cannot be restricted ... use ALLOW FILTERING
-- Bo comment de tu nhin thay thong bao loi, roi doc lai Chuong 8.
-- SELECT * FROM orders_by_customer WHERE status = 'pending';

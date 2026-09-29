-- =============================================================
-- Lab 13 data-stack — init/01-init.sql
-- Chạy tự động khi Postgres khởi tạo volume lần đầu.
-- Bảng mẫu + ít dữ liệu để có cái mà query khi làm bài tập.
-- =============================================================

CREATE TABLE IF NOT EXISTS events (
    event_id   BIGSERIAL PRIMARY KEY,
    user_id    INT         NOT NULL,
    event_type TEXT        NOT NULL,
    amount     NUMERIC(12, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ~500 dòng dữ liệu giả để query có ý nghĩa (GROUP BY, SUM, ...)
INSERT INTO events (user_id, event_type, amount, created_at)
SELECT
    1 + (g % 50),                                              -- 50 user
    (ARRAY['view','click','purchase','refund'])[1 + (g % 4)],  -- 4 loại event
    CASE WHEN g % 4 = 2 THEN (g * 997 % 500000)::numeric(12,2) -- purchase có tiền
         ELSE 0 END,
    NOW() - (g || ' minutes')::interval
FROM generate_series(1, 500) AS g;

-- View tiện cho bài tập: doanh thu theo loại event
CREATE OR REPLACE VIEW revenue_by_type AS
SELECT event_type,
       COUNT(*)      AS n_events,
       SUM(amount)   AS revenue
FROM events
GROUP BY event_type
ORDER BY revenue DESC;

# Lab 13 — Local data stack: Postgres + MinIO + Prometheus + Grafana

Dựng lại kiến trúc data platform ở quy mô local trước khi nhảy lên Kubernetes: một DB (Postgres), một object store (MinIO), và bộ monitoring (Prometheus + Grafana).

> Nguồn: trích & chuyển thể từ `13-docker-kubernetes-masterclass.html` (Module 6 Docker Compose — `docker-compose.data-stack.yml` và block profiles có Prometheus). **Không** lấy phần K8s manifests. Grafana + `prometheus.yml` + provisioning datasource là phần **tự bổ sung** để bộ monitoring chạy được ngay (bài gốc chỉ có Grafana ở mục K8s).

## Cần gì
- Docker Desktop (Compose v2).
- RAM cho Docker: **tối thiểu 3-4 GB**.
- Cổng trống: `5432` (Postgres), `9000`/`9001` (MinIO), `9090` (Prometheus), `3000` (Grafana).

## Thành phần & cổng
| Service | Image (đã pin) | UI / cổng | Đăng nhập |
|---|---|---|---|
| postgres | `postgres:16-alpine` | 5432 | `labuser` / `labpass`, db `labdb` |
| minio | `minio/minio:RELEASE.2025-04-22T22-12-26Z` | Console http://localhost:9001 | `minioadmin` / `minioadmin123` |
| prometheus | `prom/prometheus:v2.53.5` | http://localhost:9090 | — |
| grafana | `grafana/grafana:11.6.16` | http://localhost:3000 | `admin` / `admin` |

## Các bước

**1. Bật stack**
```bash
docker compose up -d
docker compose ps        # đợi postgres + prometheus (healthy), grafana (healthy)
```

**2. Mở các UI**
- MinIO Console → http://localhost:9001
- Prometheus → http://localhost:9090
- Grafana → http://localhost:3000 (datasource Prometheus đã được provision sẵn)

## Bài tập nhỏ

**A. MinIO — tạo bucket**
- Vào Console (9001) → **Create Bucket** → đặt tên `lab-bucket` → upload thử một file.
- Hoặc bằng CLI (cần cài `mc` trên máy, hoặc chạy trong container `minio/mc`):
  ```bash
  docker run --rm --network 13-data-stack_data-net minio/mc:RELEASE.2025-04-08T15-39-49Z \
    sh -c "mc alias set lab http://minio:9000 minioadmin minioadmin123 && mc mb lab/lab-bucket && mc ls lab"
  ```
  (Tên network có tiền tố theo thư mục: `docker network ls` để lấy tên chính xác.)

**B. Postgres — query dữ liệu mẫu**
```bash
docker exec -it stack-postgres psql -U labuser -d labdb -c "SELECT * FROM revenue_by_type;"
docker exec -it stack-postgres psql -U labuser -d labdb -c "SELECT event_type, COUNT(*) FROM events GROUP BY 1;"
```

**C. Prometheus / Grafana — xem metric**
- Prometheus (9090) → tab **Graph** → gõ `up` → Execute: thấy target `prometheus` = 1 (đang sống).
- Thử thêm: `prometheus_tsdb_head_series`, `rate(prometheus_http_requests_total[5m])`.
- Grafana (3000) → **Explore** → chọn datasource **Prometheus** → gõ `up` → Run. Hoặc tạo Dashboard → Panel với query trên.
- Muốn metric của Postgres thật: bỏ comment service `postgres-exporter` trong `docker-compose.yml` **và** job `postgres` trong `prometheus/prometheus.yml`, rồi `docker compose up -d`. Query thử `pg_up`, `pg_stat_database_numbackends`.

**Dọn dẹp**
```bash
docker compose down -v
```

## Vì sao pin đúng tag MinIO tháng 4/2025
Các bản MinIO community mới hơn (khoảng giữa 2025) đã lược bỏ Console UI khỏi image. `RELEASE.2025-04-22T22-12-26Z` là mốc còn Console để làm được bài "tạo bucket bằng trình duyệt". Đổi sang `:latest` có thể mất luôn UI 9001 — đó là lý do **không dùng `:latest`**.

## Khi hỏng thì soi gì
> **Debug chính là bài học.**

1. **Một service không `healthy`** → xem log chính nó:
   ```bash
   docker compose logs prometheus | tail -40
   docker compose logs grafana | tail -40
   docker compose logs minio | tail -40
   ```

2. **Grafana không thấy dữ liệu** → kiểm tra datasource:
   - Grafana → Connections → Data sources → Prometheus → **Save & test** (phải xanh).
   - URL phải là `http://prometheus:9090` (tên service, **không** `localhost` — vì Grafana ở trong network Docker, `localhost` là chính nó).

3. **Prometheus target DOWN** → http://localhost:9090/targets. Nếu bật postgres-exporter mà target đỏ: kiểm tra `DATA_SOURCE_NAME` và service exporter đã chạy chưa.

4. **Cổng bị chiếm** (`bind: address already in use`) → đổi cổng host bên trái dấu `:` trong `ports:`, hoặc tắt tiến trình đang giữ cổng đó.

5. **`prometheus.yml` sai cú pháp** → Prometheus sẽ không start; log in rõ dòng lỗi YAML. Sửa rồi `docker compose restart prometheus`.

## Ghi chú trung thực
YAML (compose + prometheus.yml + provisioning) và SQL đã được **validate tự động** (yaml.safe_load, sqlparse). **Chưa chạy trên Docker thật** trong môi trường tạo ra nó. Gặp lỗi khi `up` → đọc log, sửa, ghi postmortem. Đó là phần thực hành.

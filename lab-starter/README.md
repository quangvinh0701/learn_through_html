# lab-starter — scaffolding chạy-được cho 4 lab lớn DE Masterclass

Thư mục này là **giàn giáo (scaffolding) chạy standalone** cho bốn lab nặng nhất của bộ tài liệu. Mục tiêu: bạn chỉ cần **Docker Desktop** và một lệnh `docker compose up` — thay vì copy từng block code từ file HTML rồi tự ghép.

Nội dung ở đây được **trích và chuyển thể** từ các file HTML đã vá trong bộ tài liệu (không bịa lại từ đầu); những chỗ HTML để lửng (image tag, healthcheck, `depends_on`, volume) đã được điền để thành file chạy được.

## Yêu cầu chung
- **Docker Desktop** (Windows/macOS/Linux) đang chạy, dùng **Compose v2** (`docker compose`, không phải `docker-compose`).
- **RAM cấp cho Docker**: khuyến nghị **6-8 GB** để chạy thoải mái (đặc biệt lab CDC với Kafka). Tối thiểu 4 GB cho từng lab chạy riêng.
- Đĩa trống ~5-8 GB cho image.
- Windows: dùng **WSL2 backend**; các script `.sh` chạy trong **Git Bash** hoặc **WSL**.
- Chạy **từng lab một** (đừng bật cả bốn cùng lúc trừ khi máy khỏe) — có vài lab cùng dùng cổng `5432`.

## Thứ tự học đề xuất
1. **`13-data-stack/`** — dễ nhất, làm quen Compose + healthcheck + UI (Postgres, MinIO, Prometheus, Grafana). Không có gì phải "đăng ký" thủ công.
2. **`12-airflow/`** — một Airflow 3 tối giản: chạy DAG E2E self-contained + xem Assets (data-aware scheduling).
3. **`11-cdc-kafka/`** — khó nhất, nhiều tầng: Postgres → Debezium → Kafka. Đây là chỗ bạn sẽ debug nhiều nhất (và học nhiều nhất).
4. **`27-nosql/`** — bốn hệ lưu trữ song song (Redis, MongoDB, Cassandra, DynamoDB Local). Nặng RAM chứ không nặng cấu hình; giá trị nằm ở việc so sánh cùng một bài toán trên bốn mô hình dữ liệu.

| Lab | Thư mục | Chạy nhanh |
|---|---|---|
| CDC → Kafka | [`11-cdc-kafka/`](./11-cdc-kafka/) | `docker compose up -d` → `bash register-connector.sh` → `bash consume.sh` |
| Airflow 3 + Assets | [`12-airflow/`](./12-airflow/) | `docker compose up -d` → http://localhost:8080 |
| Data stack | [`13-data-stack/`](./13-data-stack/) | `docker compose up -d` → mở các UI |
| NoSQL 4 hệ | [`27-nosql/`](./27-nosql/) | `docker compose up -d` → `docker exec nosql-cassandra cqlsh -f /schema/cassandra-schema.cql` → `python3 scripts/dynamodb_setup.py` |

Mỗi thư mục có `README.md` riêng với các bước chi tiết và mục **"Khi hỏng thì soi gì"**.

## Image tags — đã PIN cụ thể (không `:latest`)
| Image | Tag | Dùng ở lab |
|---|---|---|
| postgres | `16-alpine` | 11, 12, 13 |
| confluentinc/cp-zookeeper | `7.6.12` | 11 |
| confluentinc/cp-kafka | `7.6.12` | 11 |
| debezium/connect | `2.7.3.Final` | 11 |
| apache/airflow | `3.0.3` | 12 |
| minio/minio | `RELEASE.2025-04-22T22-12-26Z` | 13 |
| prom/prometheus | `v2.53.5` | 13 |
| grafana/grafana | `11.6.16` | 13 |
| *(tùy chọn)* provectuslabs/kafka-ui | `v0.7.2` | 11 |
| *(tùy chọn)* quay.io/.../postgres-exporter | `v0.15.0` | 13 |
| redis | `7-alpine` | 27 |
| mongo | `7.0` | 27 |
| cassandra | `4.1` | 27 |
| amazon/dynamodb-local | `2.6.1` | 27 |

Tất cả tag trên đã được kiểm tra tồn tại trên Docker Hub (tháng 7/2026; `redis:7-alpine` và `amazon/dynamodb-local:2.6.1` được đối chiếu lại qua Docker Hub API ngày 2026-07-30). Pin tag = build có thể tái lập; `:latest` là cách nhanh nhất để "hôm qua chạy, hôm nay hỏng".

## Triết lý: "debug là bài học"
Bốn lab này cố tình **không** được bọc trong một script "bấm là xong". Lý do:

> Data engineering thực tế là chuỗi những lần một service không lên, một connector FAILED, một target Prometheus DOWN. Giá trị nằm ở việc bạn **đọc được log, khoanh vùng được tầng hỏng, và sửa**. Nếu mọi thứ luôn chạy trơn, bạn chẳng học được gì về vận hành.

Vì vậy mỗi lab README có mục **"Khi hỏng thì soi gì"** — không phải để bạn tránh lỗi, mà để bạn biết soi ở đâu khi (chứ không phải nếu) gặp lỗi. Gặp lỗi → sửa → viết một **postmortem** ngắn: *triệu chứng → nguyên nhân → cách sửa*. Đó mới là sản phẩm của lab.

## Ghi chú trung thực (quan trọng)
**Cú pháp đã được validate tự động** — mọi `.yml` qua `yaml.safe_load`, mọi `.sh` qua `bash -n`, SQL qua `sqlparse`, DAG Python qua `python3 -m py_compile`, JavaScript seed của Mongo qua `node --check`. Riêng lab 27, logic của `dynamodb_setup.py` còn được **chạy thật** trên backend giả lập `moto` (`scripts/test_logic.py`) — CQL thì chỉ soát bằng mắt vì không có parser CQL. **Nhưng chưa chạy trên Docker thật** (môi trường tạo ra scaffolding này không có Docker daemon). Nếu bạn `docker compose up` và gặp lỗi, **đó là phần bài tập của bạn**: đọc log, sửa, và ghi lại postmortem.

Những chỗ đã chủ động **sửa khác với HTML** (vì bản HTML có lỗi nhỏ hoặc để lửng) được ghi chú ngay trong file tương ứng — ví dụ: tên topic CDC đúng là `cdc.public.orders` (HTML ghi dư `dbserver`), dạng `command` của Postgres, healthcheck MinIO dùng HTTP endpoint thay vì `mc`.

# Lab 11 — CDC: PostgreSQL → Debezium → Kafka

Bắt mọi thay đổi (INSERT/UPDATE/DELETE) trong Postgres và phát thành event stream trên Kafka, **không** để application tự emit. Debezium đọc WAL của Postgres qua logical replication.

> Nguồn: trích & chuyển thể từ `11-streaming-data-api-masterclass.html` (Module 3 và Module 13 Lab). Phần FastAPI + WebSocket + Redis của lab gốc **không** nằm ở đây — scaffolding này tập trung đúng khúc xương sống CDC → Kafka để bạn thấy event chảy.

## Cần gì
- Docker Desktop đang chạy (Compose v2).
- RAM: cấp cho Docker **tối thiểu 4 GB** (Kafka + ZK + Connect + Postgres). 6 GB thì mượt.
- Cổng trống trên host: `5432`, `9092`, `8083` (và `8085` nếu bật Kafka UI).
- `curl` + `bash` để chạy `register-connector.sh` (Windows: dùng Git Bash hoặc WSL).

## Thành phần & cổng
| Service | Image (đã pin) | Cổng host | Vai trò |
|---|---|---|---|
| postgres | `postgres:16-alpine` | 5432 | Source DB, `wal_level=logical` |
| zookeeper | `confluentinc/cp-zookeeper:7.6.12` | — | Metadata cho Kafka (xem ghi chú KRaft trong compose) |
| kafka | `confluentinc/cp-kafka:7.6.12` | 9092 | Broker, **dual-listener** 29092 (nội bộ) / 9092 (host) |
| kafka-connect | `debezium/connect:2.7.3.Final` | 8083 | Kafka Connect + Debezium, REST API |
| kafka-ui *(tùy chọn, comment)* | `provectuslabs/kafka-ui:v0.7.2` | 8085 | Soi topic bằng trình duyệt |

## Các bước

**1. Bật stack**
```bash
docker compose up -d
```

**2. Đợi tới khi mọi service healthy**
```bash
docker compose ps
# Chờ postgres, kafka, kafka-connect ở trạng thái (healthy).
# kafka-connect có start_period 30s — đừng vội, nó cần thời gian bung plugin.
```

**3. Đăng ký connector**
```bash
bash register-connector.sh
# Kỳ vọng: HTTP 201 Created, rồi status có "state":"RUNNING".
```

**4. Xem event chảy về (mở terminal riêng, để nó chạy)**
```bash
bash consume.sh                      # mặc định topic cdc.public.orders
# hoặc: bash consume.sh cdc.public.order_items
```
Ngay khi connector RUNNING với `snapshot.mode=initial`, bạn sẽ thấy **snapshot** của mấy chục dòng seed đổ ra trước, rồi tới các change sau đó.

**5. Sinh thay đổi để thấy stream (terminal thứ ba)**
```bash
# INSERT
docker exec cdc-postgres psql -U postgres -d labdb -c \
  "INSERT INTO orders (order_id, customer_id, total, status) VALUES ('ORD-9001','CUST-Z',999000,'pending');"

# UPDATE (nhờ REPLICA IDENTITY FULL, event mang cả giá trị cũ)
docker exec cdc-postgres psql -U postgres -d labdb -c \
  "UPDATE orders SET status='delivered' WHERE order_id='ORD-9001';"

# DELETE
docker exec cdc-postgres psql -U postgres -d labdb -c \
  "DELETE FROM orders WHERE order_id='ORD-9001';"
```
Cửa sổ `consume.sh` phải nhả ra 3 event tương ứng trong ~1 giây.

**6. Dọn dẹp**
```bash
docker compose down -v     # -v xoá luôn volume (mất data + replication slot)
```

## Vì sao topic tên là `cdc.public.orders`
Debezium đặt tên topic theo `<topic.prefix>.<schema>.<table>`. Connector ở đây có `topic.prefix=cdc`, bảng `public.orders` → topic `cdc.public.orders`. (Bản HTML gốc ghi nhầm `cdc.dbserver.public.orders` — dư chữ `dbserver`; đã sửa trong `consume.sh`.)

## Khi hỏng thì soi gì
> Triết lý bộ tài liệu: **debug chính là bài học**. Pipeline này có 4 tầng, hỏng ở đâu cũng để lại dấu vết. Học cách đọc dấu vết đó.

1. **Connector không lên RUNNING / FAILED**
   ```bash
   curl -s http://localhost:8083/connectors/lab-orders-connector/status | jq
   ```
   Đọc `tasks[].trace` — 90% lỗi nằm ở đây (sai user/password, chưa `wal_level=logical`, thiếu quyền REPLICATION).

2. **Log của Kafka Connect / Debezium**
   ```bash
   docker compose logs -f kafka-connect
   ```
   Tìm dòng `ERROR`. Lỗi hay gặp: `must be superuser or replication role`, `publication ... does not exist`.

3. **Replication slot & publication trong Postgres**
   ```bash
   docker exec cdc-postgres psql -U postgres -d labdb -c "SELECT * FROM pg_replication_slots;"
   docker exec cdc-postgres psql -U postgres -d labdb -c "SELECT * FROM pg_publication;"
   ```
   Slot `debezium_slot` phải tồn tại và `active=t`. Slot còn treo sau khi xoá connector là nguyên nhân kinh điển làm WAL phình to.

4. **Kafka thật sự có topic + message chưa**
   ```bash
   docker exec cdc-kafka kafka-topics --bootstrap-server localhost:9092 --list
   ```
   Không thấy `cdc.public.orders`? → connector chưa capture được, quay lại (1)(2).

5. **Nghi ngờ dual-listener?** Nếu container `kafka-connect` báo không nối được broker: kiểm tra nó dùng `kafka:29092` (nội bộ) **chứ không** `localhost:9092`. Client trên host thì ngược lại — `localhost:9092`. Nhầm hai cái này là lỗi phổ biến nhất khi tự sửa compose.

## Ghi chú trung thực
Cú pháp YAML / SQL / bash trong thư mục này đã được **validate tự động** (yaml.safe_load, sqlparse, `bash -n`). Nhưng **chưa chạy trên Docker thật** trong môi trường tạo ra nó. Nếu `docker compose up` báo lỗi, đó là phần bài tập của bạn: đọc log, sửa, và ghi lại một postmortem ngắn (triệu chứng → nguyên nhân → cách sửa).

# Lab 27 — NoSQL & Distributed Storage

Bốn hệ lưu trữ chạy song song trong một stack, để bạn so sánh **trực tiếp** cùng một bài toán trên bốn mô hình dữ liệu khác nhau: Redis (key-value), MongoDB (document), Cassandra (wide-column), DynamoDB Local (managed key-value, bản chạy máy).

> Nguồn: trích & chuyển thể từ `27-nosql-distributed-storage-masterclass.html` (Chương 8, 12, 16). Những chỗ HTML để lửng — image tag, healthcheck, giới hạn heap Cassandra, cách nạp schema CQL — đã được điền để thành file chạy được.

Bài toán xuyên suốt: **tầng lưu trữ cho một hệ thương mại điện tử**. Session và giỏ hàng vào Redis; catalog sản phẩm với thuộc tính không đồng nhất vào MongoDB; đơn hàng theo access pattern vào DynamoDB single-table; sự kiện thiết bị chuỗi thời gian vào Cassandra.

## Cần gì
- Docker Desktop đang chạy (Compose v2).
- RAM cấp cho Docker: **tối thiểu 6 GB** nếu bật cả bốn service (Cassandra một mình ăn ~2 GB). Chỉ làm phần Redis + Mongo thì 2 GB là đủ.
- Đĩa trống ~3 GB cho image.
- Python 3.9+ với `boto3` cho `scripts/dynamodb_setup.py`.
- Cổng trống trên host: `6379`, `27017`, `9042`, `8000`.

## Thành phần & cổng
| Service | Image (đã pin) | Cổng host | Vai trò trong lab |
|---|---|---|---|
| redis | `redis:7-alpine` | 6379 | Session, giỏ hàng, rate limit |
| mongo | `mongo:7.0` | 27017 | Catalog sản phẩm, thuộc tính không đồng nhất |
| cassandra | `cassandra:4.1` | 9042 | Chuỗi thời gian có bucketing, đơn theo khách |
| dynamodb-local | `amazon/dynamodb-local:2.6.1` | 8000 | Single-table design cho đơn hàng |

## Các bước

**1. Bật stack**
```bash
docker compose up -d
# Chỉ cần hai service nhẹ? docker compose up -d redis mongo
```

**2. Đợi healthy — Cassandra chậm nhất**
```bash
docker compose ps
# redis/mongo/dynamodb-local healthy trong ~20-30s.
# cassandra có start_period 90s. Nó "Up" trước khi CQL sẵn sàng —
# đừng tin cột STATUS, hãy đợi tới (healthy).
```

**3. Redis — session, giỏ hàng, rate limit**
```bash
docker exec -it nosql-redis redis-cli

HSET sess:9f3a1c user_id U-1042 role customer ip 10.0.3.7
EXPIRE sess:9f3a1c 1800
TTL sess:9f3a1c

HSET cart:U-1042 SKU-A 2
HINCRBY cart:U-1042 SKU-A 3      # 2 -> 5, một vòng, không đọc trước khi ghi
HGETALL cart:U-1042

INFO persistence                 # xem aof_enabled và rdb_last_save_time
```

**4. MongoDB — catalog đã seed sẵn**
```bash
docker exec -it nosql-mongo mongosh -u root -p rootpass --authenticationDatabase admin shop

db.products.countDocuments({})
db.products.find({category: 'electronics'}).sort({price: 1})
db.products.countDocuments({in_stock: false})          // 2
db.products.countDocuments({in_stock: {$ne: true}})    // 3  <-- khác nhau, vì sao?
db.products.find({category: 'electronics'}).sort({price: 1}).explain('executionStats')
```
Cột cần đọc trong `explain`: `totalKeysExamined`, `totalDocsExamined`, `executionTimeMillis`, và `winningPlan.stage` — `IXSCAN` là dùng index, `COLLSCAN` là quét cả collection.

**5. Cassandra — nạp schema bằng tay**
Cassandra **không** có cơ chế tự chạy script lúc khởi tạo (khác Postgres, khác Mongo). File `.cql` được mount vào `/schema`, bạn tự chạy:
```bash
docker exec nosql-cassandra cqlsh -f /schema/cassandra-schema.cql
docker exec -it nosql-cassandra cqlsh

USE shop;
SELECT order_id, created_at, total FROM orders_by_customer WHERE customer_id = 'C-01';
SELECT * FROM orders_by_customer WHERE status = 'pending';   -- SẼ BÁO LỖI, đúng như dự kiến
```

**6. DynamoDB Local — single-table**
```bash
pip install boto3
python3 scripts/dynamodb_setup.py            # tạo bảng, seed, chạy AP-5/6/7, đo Scan
python3 scripts/dynamodb_setup.py --reset    # xoá và làm lại từ đầu

# soi bằng AWS CLI nếu có
aws dynamodb list-tables --endpoint-url http://localhost:8000 \
  --region ap-southeast-1
```

**7. Dọn dẹp**
```bash
docker compose down -v      # -v xoá cả volume: mất toàn bộ data
```

## Bài tập

1. **Đo độ bền của Redis.** Sửa `command` trong compose, bỏ `--appendonly yes`, `docker compose up -d redis`. Ghi 1.000 key, `docker kill nosql-redis` (kill chứ không stop — stop cho Redis kịp lưu), bật lại, đếm còn bao nhiêu key. Lặp lại với AOF bật. Ghi lại con số cho cả hai trường hợp.
2. **Kích thước index MongoDB.** Chạy `db.products.stats().indexSizes`, thêm index cho `attrs.color` (chỉ 1/8 tài liệu có), so `sparse: true` với `sparse: false`. Chênh lệch bao nhiêu byte? Đúng như kỳ vọng không?
3. **Hot partition trong Cassandra.** Ghi 50.000 dòng vào `events_by_day_bad` (khoá phân vùng đơn điệu) và 50.000 dòng vào `events_by_device`. Chạy `nodetool tablehistograms shop.events_by_day_bad` và so phân vị kích thước phân vùng của hai bảng. Đến ngưỡng nào thì phân vùng "xấu"?
4. **Chi phí của GSI.** Sửa `scripts/dynamodb_setup.py`, đổi `Projection` từ `INCLUDE` sang `ALL`, seed lại, so `ItemCount` và `IndexSizeBytes` bằng `describe_table`. Ngoại suy sang 10 triệu đơn thì hoá đơn lưu trữ chênh bao nhiêu?
5. **Cassandra ba node** (nặng, cần ~6 GB RAM riêng cho Cassandra). Nhân service `cassandra` thành `cassandra-1/2/3`, đặt `CASSANDRA_SEEDS: cassandra-1`, đổi keyspace sang `NetworkTopologyStrategy` với `'dc1': 3`. Rồi: dừng một node, ghi ở `CONSISTENCY QUORUM`, bật lại, chạy `nodetool repair`, quan sát. Đây là bài duy nhất trong lab dạy được quorum thật.
6. **Đối soát Mongo → DuckDB.** `mongoexport` collection `products` ra NDJSON, làm phẳng bằng DuckDB theo đúng Chương 15, rồi kiểm tra: số tài liệu nguồn có bằng số `product_id` đích không, tổng số `variants` có khớp không.

## Khi hỏng thì soi gì

> Triết lý bộ tài liệu: **debug chính là bài học**. Bốn hệ, bốn kiểu hỏng khác nhau. Học cách đọc dấu vết của từng hệ.

1. **Cassandra không bao giờ `healthy`**
   ```bash
   docker compose logs cassandra | tail -50
   docker exec nosql-cassandra nodetool status
   ```
   Nguyên nhân hay gặp nhất là **thiếu RAM**: log có `OutOfMemoryError` hoặc container bị OOMKilled (`docker inspect nosql-cassandra --format '{{.State.OOMKilled}}'`). Sửa: tăng RAM cho Docker Desktop, hoặc hạ `MAX_HEAP_SIZE` xuống `768M`. Nguyên nhân thứ hai: khởi động chưa xong thật — Cassandra 4.1 cần 60-90 giây trên máy thường; `start_period: 90s` là cố ý.

2. **`cqlsh -f` báo `Unable to connect to any servers`**
   Container "Up" nhưng CQL chưa mở cổng 9042. Đợi tới khi `docker compose ps` báo `(healthy)` rồi hãy chạy.

3. **MongoDB không thấy dữ liệu seed**
   Script trong `/docker-entrypoint-initdb.d` **chỉ chạy một lần**, lúc volume trống. Nếu bạn đã `up` trước khi có file seed, volume đã khởi tạo rồi.
   ```bash
   docker compose down -v && docker compose up -d mongo
   docker compose logs mongo | grep -A5 "mongo-seed"
   ```

4. **MongoDB báo `Authentication failed`**
   Có `MONGO_INITDB_ROOT_USERNAME` nghĩa là auth đã bật. Phải truyền đủ:
   `mongosh -u root -p rootpass --authenticationDatabase admin shop`.

5. **`dynamodb_setup.py` báo `Could not connect to the endpoint URL`**
   ```bash
   docker compose ps dynamodb-local
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000   # 400 là BÌNH THƯỜNG
   ```
   DynamoDB Local trả HTTP 400 cho request GET rỗng — nhận được 400 tức là nó đang sống. Không nhận được gì mới là hỏng.

6. **DynamoDB Local: bảng "biến mất" giữa các lần chạy**
   Thiếu cờ `-sharedDb`. Không có nó, DynamoDB Local tạo **một file DB riêng cho mỗi cặp access-key + region**; đổi credential là như đổi tài khoản. Compose ở đây đã bật `-sharedDb`.

7. **`TransactionCanceledException` với lý do vô nghĩa**
   Nếu bạn tự viết lại code và gọi `transact_write_items` qua `resource.meta.client`: đó là lỗi. `boto3.resource('dynamodb')` gắn thêm bộ chuyển đổi kiểu lên chính client của nó, nên `AttributeValue` bạn viết sẵn (`{"S": "..."}`) bị bọc thêm một lớp. Dùng `boto3.client('dynamodb', ...)` riêng — xem `get_client()` trong `dynamodb_setup.py`. Lỗi này đã gặp thật khi dựng scaffolding này (moto báo `TypeError: unhashable type: 'dict'`).

8. **Redis mất dữ liệu sau khi restart**
   Đó là hành vi **đúng** nếu AOF tắt. `docker exec nosql-redis redis-cli INFO persistence` và đọc `aof_enabled`, `rdb_last_save_time`, `rdb_changes_since_last_save`. Đây là nội dung Bài tập 1, không phải lỗi.

9. **Cổng bị chiếm**
   `6379`, `27017`, `9042`, `8000` hay va với dịch vụ có sẵn trên máy (nhất là `8000`). Đổi vế trái của `ports:` — ví dụ `"8010:8000"` — rồi chạy `python3 scripts/dynamodb_setup.py --endpoint http://localhost:8010`.

## Ghi chú trung thực

**Đã validate tự động, trong môi trường tạo ra thư mục này:**
- `docker-compose.yml` — `yaml.safe_load` đạt; 4 service, 4 volume, cả 4 đều có healthcheck.
- `init/mongo-seed.js` — `node --check` đạt (cú pháp JavaScript hợp lệ).
- `scripts/dynamodb_setup.py`, `scripts/test_logic.py` — `python3 -m py_compile` đạt.
- **Logic của `dynamodb_setup.py` đã CHẠY THẬT** với backend giả lập `moto`: tạo bảng, seed 19 item, ba access pattern, `TransactWriteItems` thành công lần đầu và bị từ chối lần hai, số đơn `pending` giảm từ 3 xuống 2. Chạy lại bằng `python3 scripts/test_logic.py` (cần `pip install "moto[dynamodb]"`).
- `init/cassandra-schema.cql` — soát bằng mắt cộng kiểm tra cơ học: cân bằng `()`/`{}`/`[]`, số nháy đơn chẵn, 22 câu lệnh (6 CREATE, 9 INSERT, 3 SELECT, 2 UPDATE, 1 DROP, 1 USE). **Không có parser CQL nào chạy trên nó.**

**Chưa làm:**
- **Chưa chạy trên Docker thật.** Môi trường tạo ra scaffolding này không có Docker daemon. Nếu `docker compose up` báo lỗi, đó là phần bài tập của bạn: đọc log, sửa, ghi postmortem ngắn (triệu chứng → nguyên nhân → cách sửa).
- Tag `redis:7-alpine` và `amazon/dynamodb-local:2.6.1` đã **đối chiếu với Docker Hub API ngày 2026-07-30** (tồn tại, `tag_status: active`). Tag `mongo:7.0` và `cassandra:4.1` là tag official-image chuẩn nhưng **chưa đối chiếu lại** trong lần dựng này.
- `moto` **không** mô phỏng trung thực `ConsumedCapacity` (nó trả cố định 1.0 RCU cho mọi thao tác, kể cả `Scan` đọc 19 item). Muốn đo dung lượng thật thì phải chạy trên AWS thật; trên DynamoDB Local hãy đọc `ScannedCount` thay vì `ConsumedCapacity`.

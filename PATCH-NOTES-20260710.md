# Patch Notes — 10/07/2026

Vá toàn bộ lỗi đã xác nhận trong báo cáo đánh giá (`DANH-GIA-BO-TAI-LIEU-DE.md`). Backup nguyên trạng trước khi vá: `_backup-before-patch-20260710/`.

## Thay đổi cấu trúc bộ tài liệu

- **MỚI: `23-dbt-analytics-engineering-masterclass.html`** (~215KB, 14 module + quiz) — lấp lỗ hổng coverage lớn nhất (dbt ~61% JD). Điểm khác biệt so với phần còn lại của bộ: **lab module 13 là code đã chạy thật** — project dbt-duckdb được dựng và chạy trong sandbox, `dbt build` PASS 25/25 (dbt Core 1.11 + dbt-duckdb 1.10), output trong bài là output thật. Nội dung: dbt Core/Fusion, models & ref, materializations, incremental (merge/insert_overwrite/microbatch 1.9+), tests + unit tests (1.8+), snapshots YAML 1.9, docs/lineage, Jinja/macros, contracts & governance, production (slim CI `state:modified+ --defer`, GitHub Actions, Cosmos), semantic layer/MetricFlow, cheatsheet + quiz.
- **`_19-mlops-platform-masterclass.html` → `24-mlops-platform-masterclass.html`** — đưa file MLOps (chất lượng 8/10, trước đây mồ côi ngoài index) vào lộ trình chính thức làm phụ lục.
- **`00-index.html`**: thêm entry 23 + 24, cập nhật "24 masterclass".
- **`masterclass-all-in-one.html`**: rebuild bằng `build.py` — giờ gộp đủ 24 file (7.1MB).
- Lưu ý: `index.html` và `masterclass-protected.html` là bản mã hóa mật khẩu của file gộp CŨ — cần tự chạy lại: `python make-protected.py "MatKhau" masterclass-all-in-one.html index.html` (tôi không có mật khẩu). `masterclass-de-only.html` là bản build cũ (6/2026), đã lỗi thời so với bản vá — cân nhắc xóa hoặc rebuild.

## Lỗi đã vá theo file (86 fix, tất cả grep-verify sau khi sửa)

### 01 — Linux (4 fix)
CRON_TZ ghi rõ chỉ có ở cronie/RHEL, Ubuntu/Debian dùng systemd timer; `ls *.csv | xargs` → `find -print0 | xargs -0`; thêm `sudo` cho sysctl; script daily_etl bản "mindset" thêm `set -euo pipefail` + quote biến.

### 02 — PostgreSQL (4 fix)
Thêm `CREATE EXTENSION btree_gist` trước EXCLUDE constraint; sửa TRUNCATE không reset identity (cần RESTART IDENTITY); caveat benchmark vendor pgvectorscale; điều kiện COPY tối ưu WAL (wal_level=minimal + bảng cùng transaction).

### 03 — Business Domain (5 fix)
DAU/MAU×30 = số ngày active (không phải sessions); xóa biểu thức DAU/MAU×MAU vô nghĩa; điều kiện K<1 cho CAC hiệu dụng; sửa nhãn BCBS 239 Adaptability; thay 3 placeholder "scn" + typo "đối chếu".

### 04 — Data Pipeline (6 fix)
Bọc subquery cho `WHERE rn = 1`; sửa 2 chỗ Spark overwrite cùng path (→ path tạm + swap atomic); thay `retry_if_status` (không tồn tại trong tenacity) bằng `retry_if_exception` đúng; `RENAME TO` bỏ schema-qualified; tình huống BigQuery dùng lệnh BigQuery (`bq cancel`, `maximum_bytes_billed`) thay ALTER WAREHOUSE; thêm box Airflow 3.0 (execution_date bị loại, Datasets→Assets).

### 05 — Spark (5 fix)
**Salting sửa lỗi NULL toàn bộ**: `col + lit("_") + col` → `concat_ws` (cả 2 chỗ) + sửa ngoặc + import; **Delta streaming sink bỏ outputMode("update") trực tiếp** → foreachBatch + MERGE (2 chỗ); thêm alias cho stream-stream join; sửa ví dụ "Thảm hoạ A" để code hợp lệ mà vẫn đúng bài học; xóa ghi chú tác giả lọt vào bài.

### 06 — Data Modeling (8 fix)
Sửa fact giới hạn partition (Snowflake tự quản, BigQuery 10.000); DDL thống nhất BigQuery thuần; PIT chuyển half-open interval + bỏ cột sai cú pháp; `COUNT(DISTINCT customer_sk)` → đếm natural key qua join dim (2 chỗ); sửa mô tả Knight Capital đúng lịch sử (3 chỗ); sửa Chamberlin/Codd; chú thích pseudo-code cho `next_sk()`; thêm box lakehouse modeling trỏ Masterclass 16.

### 07 — Modeling for Serving (5 nhóm fix)
Grain fact_orders nhất quán (order-level); bỏ nhãn SCD2 giả + xóa tham chiếu `is_current` không tồn tại; lab chạy được với Postgres thật (bỏ TRY_TO_TIMESTAMP, CURRENT_TIMESTAMP(), cluster_by, 3-part name); **viết lại toàn bộ code Cube.dev theo API thật** (cubejs-cli, env CUBEJS_DB_*, refreshKey, rollupJoin, REST order format, bỏ SDK Python bịa); incremental lookback dùng `MAX(...) FROM {{ this }}`.

### 08 — WebAPI (7 fix)
**Sửa khái niệm async/sync bị đảo ngược** (blocking trong `async def` mới giết event loop); LoadTestShape mốc cộng dồn; `JSONResponse(status_code=, content=)` (2 chỗ); bỏ `await create_async_engine`; `datetime.now(timezone.utc)`; note passlib ngừng maintain; sửa heading lặp module 07.

### 09 — Data API Patterns (7 fix)
Order thành SQLAlchemy model đúng + đảo rows nhánh `before`; `aiodataloader`/`batch_load_fn`; tách block Python/JS + đúng package complexity; sửa `type OrderStatus`; export worker streaming thật (yield_per + chunk) thay buffer 1M rows; rate limiter tính cost thật; bỏ route trùng + sửa Link header.

### 10 — Data Quality (4 nhóm fix — file được sửa nặng nhất)
**Sửa toàn bộ "loạn chữ" tiếng Việt** (~15 cụm: "yên tím", "bất chợp", "Mộng pipeline", "TìNH HUŐNG", "Ùy ban threshold"...); **viết lại Great Expectations theo GX Core 1.x thuần nhất** (bỏ trộn 3 thế hệ API + expectation bịa); **viết lại Pact theo pact-python thật** (given/upon_receiving/with_request/will_respond_with, Term/Like/EachLike, verify_with_broker); bảng breaking change dùng ✓/✗ nhất quán.

### 11 — Streaming (9 fix)
`enable_auto_commit=False` cho 5 consumer commit thủ công; Debezium `PostgresConnector` (3 chỗ) + bỏ `database.server.name`; `SerializingProducer`/`DeserializingConsumer` cho Avro; bỏ `[default]` trong proto3; SSE `retry:` chuyển vào body stream; **sửa docker-compose Kafka dual-listener đúng chuẩn** (cả 2 compose + trỏ lại client nội bộ sang kafka:29092); thay RLS sai cú pháp bằng `REPLICA IDENTITY FULL` (thứ CDC thật sự cần); cập nhật KRaft (3.3, Kafka 4.0 bỏ ZK).

### 12 — Airflow (6 nhóm fix)
Lab E2E parse được: thêm/bỏ import đúng, provider path cho PostgresHook, stub slack_failure_alert, **sửa bẫy Jinja `{{ ds }}` trong thân hàm Python**, sửa signature success_alert; thay GE API cổ bằng check pandas chạy được; chú thích catchup default đổi ở Airflow 3; sửa "Prefect Orion"; **thêm mục mới "Assets & data-aware scheduling"** (cú pháp Airflow 3: `@asset`, `schedule=[Asset(...)]`); sửa bảng so sánh với Dagster.

### 13 — Docker/K8s (7 fix)
Xóa ký tự Trung Quốc + dòng "KDying" rác (→ PSI, memory.oom.group); sửa fact cgroup v1/K8s 1.31; bỏ `pip --user --prefix` xung đột; K8s `command` dạng mảng; bỏ `restartPolicy: Always` khỏi init containers; MinIO StatefulSet distributed mode + pin tag; note phiên bản kind/Airflow.

### 14 — AWS (5 fix)
**CI/CD chuyển sang OIDC** (bỏ static keys — nhất quán với Masterclass 17); GlueVersion 5.0; EMR 7.5.0; typo athena-cur; bỏ số liệu audit bịa.

### 15 — GCP (4 nhóm fix)
**Sửa fact Managed Kafka** (GA cuối 2024); bảng GCS 4 class + Autoclass là tính năng; **sửa 4 lỗi API Beam** (subscription-only, Timestamp.now, Repeatedly, table=); **sửa DAG Composer** (bỏ TaskFlow import bịa, @task đúng, destination_bucket/object, BigQueryInsertJobOperator, BeamRunPythonPipelineOperator, schedule=).

### 16 — Lakehouse (1 fix)
Bump version pins: Iceberg 1.7.1, Delta 3.3.0, Hudi 1.0.1 (khớp mục "Chuyển động 2024-2025" của chính file).

### 17 — Platform (1 fix)
Sửa block HCL ports đúng format (OpenTofu đã có sẵn trong file — không thêm trùng).

### 18 — System Design (1 fix)
Typo "phân tfán"; quét từ vỡ toàn file — sạch.

### 19 — DuckDB (7 fix)
**Sửa 5 chỗ params positional** (`params=` keyword — đã chạy thử thật với duckdb 1.5: OK); `INTERVAL (?) DAY` (chạy thử OK); cheatsheet thêm FROM; footer "Hết module 19"; 2 typo; bump pins (duckdb>=1.3, pyarrow>=17, polars>=1.0); capstone định nghĩa đủ biến/env/stub.

### 20 — Snowflake/Databricks (9 fix — vùng hallucination nặng nhất)
Viết lại Dynamic Tables đúng cú pháp (4 chỗ, bỏ tự tham chiếu + ngoặc bịa); **thay `CREATE SEMANTIC MODEL` + `CORTEX.CORTEX_ANALYST` bịa bằng YAML trên stage + REST API thật**; `DYNAMIC_TABLE_REFRESH_HISTORY()`; sửa UniForm (enabledFormats, thư mục metadata/, CREATE ICEBERG TABLE + catalog integration); **thay `CREATE VECTOR INDEX` bịa bằng VectorSearchClient SDK thật** + similarity_search; sửa DLT decorator chồng + F.sum; sửa tên config io cache; chú thích tên model Cortex.

### 21 — Python SWE (2 fix)
aiohttp ClientTimeout; bump ruff-pre-commit.

### 22 — GenAI (1 fix)
Chú thích "(tên model minh hoạ)" cho ví dụ MotherDuck (claim semantic layer đã có sẵn điều kiện — không sửa).

### 24 — MLOps (1 fix)
Bỏ con số cứng "18 masterclass" ở mở đầu.

## Những gì CHƯA làm (có chủ đích)

1. **Khử trùng lặp lớn** (07 nửa đầu vs 06, module 22 của file 02, khối "Lý thuyết mở rộng" file 06): cắt hàng chục KB nội dung bằng máy có rủi ro phá cấu trúc tab/anchor — nên làm tay khi đọc đến, có báo cáo đánh giá làm bản đồ.
2. **Dataset/repo scaffolding chung cho cả bộ**: lab dbt (Masterclass 23) đã có project chạy được làm hạt nhân; các lab khác vẫn cần dựng môi trường thật (Docker) — ngoài phạm vi vá file HTML.
3. Bổ sung bài tập cho file 21 và benchmark có nguồn cho file 19 — là viết mới nội dung, không phải vá lỗi.

## Cách kiểm tra lại

Mở `00-index.html` (đủ 24 module) hoặc `masterclass-all-in-one.html`. Mọi fix đều đã grep-verify; riêng code DuckDB (file 19) và toàn bộ lab dbt (file 23) đã **chạy thử thật** trong sandbox.

---

# Round 2 — 11/07/2026 (file yếu nhất + trùng lặp 07/06)

- **File 10 (Data Quality)**: toàn bộ code GX chạy kiểm chứng với GX Core 1.18 (PASS 8/8, sửa thêm 2 lỗi sót: param KL-divergence bịa, CLI đã bị bỏ); Pact viết lại theo pact-python 3.4 (API v3) — chạy thật cả consumer lẫn provider; thêm mục **Soda Core** (SodaCL chạy thật trên DuckDB 4/4 PASS); quét sửa thêm 17 lỗi loạn chữ. Output trong bài giờ là output thật.
- **File 07 (Modeling for Serving)**: tái cấu trúc khử trùng với file 06 — ~27KB nội dung dạy lại (star schema/SCD/wide-vs-star) gộp thành module "Ôn nhanh nền tảng modeling" (bảng tra cứu + tham chiếu đúng module của 06); thêm module mới **"Query patterns & hiệu năng cho BI serving"** (top-N, MoM + date spine, running total, cohort, bẫy fan-out SCD2 với demo bằng số thật, pre-aggregation trade-off, EXPLAIN cho dashboard) — SQL verify bằng DuckDB; sửa 56 anchor gãy có sẵn.

# Round 3 — 12/07/2026 (khử trùng lặp toàn bộ + nâng cấp file mỏng)

**Khử trùng lặp:**
- **File 02**: module 22 (trùng ~70% M6-7) viết lại thành "Ôn tập EXPLAIN & Index" dạng bảng + tham chiếu; giữ phần độc nhất (Hash/GiST, bảng sargability, góc Big-O); sửa "Bản đồ 21 module" → 23. (−11KB)
- **File 06**: rà cả 21 khối "Lý thuyết nền tảng mở rộng" — xóa 10 khối lặp nguyên văn, cắt tỉa 11 khối (giữ 19 mục lý thuyết độc nhất thật: functional dependency, lossless-join, Design by Contract, columnar-compression-justification...). **−84KB (−24%)**, sửa 1 thẻ `</a>` thiếu có sẵn.
- **Series 08-11**: schema evolution quy về file 10 (canonical), SSE quy về file 11, observability/healthcheck quy về file 08 — các bản lặp co thành recap + box "Tham chiếu"; phần đặc thù từng file (Schema Registry modes, SSE cho export, SLO data-API) giữ nguyên; sửa 2 anchor gãy có sẵn trong file 11. Code đã vá ở round trước không bị đụng (marker check PASS).
- **File 24 (MLOps)**: chương 12-14 (chồng ~70% lên file 22) gộp thành MỘT chương "LLMOps từ góc platform — phần bù cho Masterclass 22" — giữ phần platform đặc thù (KV cache/continuous batching, vLLM/TGI/TensorRT-LLM, kinh tế GPU + điểm hòa vốn self-host vs API, fine-tune như training pipeline), 17→15 module, 9 con trỏ sang Masterclass 22. (−30KB)

**Nâng cấp nội dung (code đều chạy thật trong sandbox trước khi ghi):**
- **File 21 (Python SWE)**: 7→10 chương. Thêm chương **"Logging & Observability cho pipeline Python"** (logging hierarchy/dictConfig, 3 bẫy kinh điển gồm duplicate handler + multiprocessing QueueHandler, structlog JSON với output thật, correlation id xuyên DAG); thêm **bài tập 3 mức cho cả 8 chương** (tiêu chí tự kiểm đo được); thêm **capstone `pipeline-runner`** (đề bài + skeleton + rubric 4 mức nộp); thêm **quiz 10 câu**. +55% dung lượng — hết là file mỏng nhất bộ.
- **File 03 (Business Domain)**: thêm **Module 22 — Lab SQL thực hành**: schema e-commerce sinh dữ liệu tất định bằng DuckDB (~148k dòng, có seasonality/churn/whale cài sẵn) + 5 lab (cohort retention, RFM/NTILE, LTV × gross margin vs công thức ARPU/churn, churn & survival & NRR, funnel mobile vs web) — mỗi lab có đề, gợi ý, lời giải trong `<details>`, output thật, bẫy diễn giải. Toàn bộ SQL trích ngược từ HTML chạy lại PASS. (+40KB)
- **File 01**: thêm box tuyên bố phiên bản hiện hành (Ubuntu 24.04 LTS / kernel 6.8 / Python 3.12, lệnh tương thích cả 22.04).
- **File 19**: 4 bảng benchmark gắn nhãn "(số minh hoạ để so sánh bậc độ lớn — tự đo với dữ liệu của bạn)".

**Dọn dẹp:** `masterclass-de-only.html` (bản build cũ 6/2026) + 2 file tạm chuyển vào `_archive/`. Backup round 3: `*-before-round3.html` trong `_backup-before-patch-20260710/`; series 08-11 có thêm `_backup-before-dedup-20260712/`.

**Trạng thái cuối:** 24 file lẻ (5.3MB) + `masterclass-all-in-one.html` (7.1MB) + 2 bản mã hóa (mật khẩu 0701, đã giải mã kiểm chứng khớp 100%). Parse check bs4 sạch toàn bộ: tab == panel, 0 anchor mồ côi.

---

# Round 4 — 12/07/2026 (runtime-verify + lab-starter + QA cross-reference)

**Runtime-verify bằng môi trường thật trong sandbox:**
- **File 05 (Spark)** — PySpark 3.5.3 + delta-spark 3.2.0 local: salting PASS (join khớp 100k dòng, hot key trải 16 ckey), Thảm hoạ A PASS (2 bản tương đương), AQE configs PASS, foreachBatch + MERGE PASS (upsert không nhân đôi; xác nhận `outputMode("update")` đi cùng foreachBatch là HỢP LỆ), stream-stream join alias PASS. 1 fix: block off-heap dùng `spark.conf.set` lúc runtime sẽ ném `CANNOT_MODIFY_CONFIG` → viết lại dạng `SparkSession.builder.config(...)`.
- **File 15 (Beam)** — apache-beam 2.75 DirectRunner: pipeline batch + dead-letter chạy end-to-end. 2 bug MỚI bắt được nhờ chạy thật: `.with_outputs('good','bad', main='main')` làm unpack 2 biến nổ (bỏ `main=`); `beam.ReadFromPubSub` không tồn tại ở top-level (→ `beam.io.ReadFromPubSub`). Mọi construct streaming (trigger/window/WriteToBigQuery kwargs) verify bằng khởi tạo thật/inspect.signature.
- **File 12 (Airflow)** — apache-airflow 3.3.0 + providers: lab DAG **DagBag parse 0 lỗi, đủ 7 task, dependency đúng**. Fixes: import path `amazon.aws.sensors.s3` (3 chỗ, bỏ S3PrefixSensor đã bị gộp), `execution_timeout` phải là timedelta, viết lại ví dụ deferrable sai bản chất (PythonOperator return Trigger không defer được → `S3KeySensor(deferrable=True)` + `TimeDeltaSensorAsync`, verify import trên Airflow 3.3 thật), sửa 2 TOC entry mồ côi có sẵn (m4/m8). Assets demo + Cosmos DbtDag parse/signature PASS, không cần sửa.

**Mới: thư mục `lab-starter/`** — scaffolding chạy standalone cho 3 lab lớn (thứ duy nhất còn thiếu theo báo cáo gốc):
- `11-cdc-kafka/`: compose ZK+Kafka dual-listener + Postgres (wal_level=logical) + Debezium Connect, init.sql (REPLICA IDENTITY FULL), register-connector.sh, consume.sh.
- `12-airflow/`: Airflow 3.0.3 standalone + DAG lab self-contained + assets_demo.py.
- `13-data-stack/`: Postgres + MinIO + Prometheus + Grafana (datasource provision sẵn).
Image tags pin cụ thể (kiểm tra tồn tại trên Docker Hub), YAML/bash/SQL/Python validate tự động. README mỗi lab có mục "Khi hỏng thì soi gì". Trung thực: chưa chạy trên Docker daemon thật — phần debug là bài tập của người học. Box note trỏ tới lab-starter đã thêm vào file 11, 12, 13.

**QA cross-reference toàn bộ 24 file:** quét 1084 match tham chiếu chéo → nội dung các file đã sạch từ các round trước (0 con trỏ lệch); cập nhật 3 mô tả trong 00-index (03 thêm Lab SQL, 07 đổi Query Patterns, 21 thêm Logging/Capstone); **phát hiện và khôi phục 00-index.html bị cắt cụt phần JS** từ một edit trước đó (lỗi làm hỏng navigation của trang hub — đã restore nguyên vẹn từ backup).

# Round 7 — 30/07/2026 (Masterclass 27 — NoSQL &amp; Distributed Storage)

**Mới: `27-nosql-distributed-storage-masterclass.html`** (~529KB, 16 chương + quiz, ~65.900 từ) — lấp lỗ hổng NoSQL: trước đó nội dung chỉ rải rác (CAP khái quát ở MC18, DynamoDB mức dịch vụ ở MC14, Redis như cache ở MC09/11), và hoàn toàn thiếu *data modeling cho NoSQL*.

Cấu trúc: (1) Vì sao NoSQL tồn tại — bốn họ, ba huyền thoại (schema-on-read, "nhanh hơn SQL", "thay thế RDBMS"), khi nào KHÔNG dùng; (2) CAP phát biểu đúng và ba hiểu lầm, PACELC, phổ mô hình nhất quán, session guarantees; (3) Nhân bản & quorum — R+W>N và vì sao vẫn không đủ cho linearizability, hinted handoff, Merkle tree, vector clock, CRDT; (4) Phân mảnh — consistent hashing, virtual node, hot partition, chỉ mục cục bộ vs toàn cục; (5) LSM-tree vs B-tree — compaction STCS/LCS/TWCS, ba loại khuếch đại, bloom filter, tombstone; (6) Redis; (7) MongoDB — nhúng vs tham chiếu, mẫu bucket/subset/computed, quy tắc ESR, shard key; (8) Cassandra — query-first design, giới hạn partition, anti-pattern; (9) DynamoDB & single-table design đầy đủ; (10) Graph & Search — BM25, khi nào graph thắng; (11) NewSQL & hội tụ; (12) Anti-pattern & tiến hoá lược đồ; (13) Giao dịch phân tán — 2PC, saga, outbox; (14) Vận hành & chi phí; (15) NoSQL trong pipeline dữ liệu; (16) Lab + capstone; quiz 10 câu.

**Kiểm chứng:** Redis chạy trên server thật (redislite nhúng redis-server 6.2); DynamoDB chạy thật qua moto (11 access pattern single-table bằng `query`, GSI/LSI, transaction); MongoDB qua mongomock; Cassandra mô phỏng bố cục partition bằng mmh3 (đúng hàm băm Cassandra dùng) — phần CQL/Cypher ghi rõ "đối chiếu tài liệu, không chạy trong sandbox", không bịa output. Các mô phỏng Python thuần cho quorum, vector clock, CRDT, consistent hashing, LSM compaction, saga, outbox đều chạy thật.

Nhiều phát hiện ngược trực giác được giữ nguyên và viết thành bài học: `SCAN` chậm hơn `KEYS` về thời gian tường (đổi thông lượng lấy độ trễ đuôi, không phải nhanh hơn); graph chỉ nhanh hơn nested-loop có chỉ mục 1,3× ở độ sâu 3 và *thua* ở độ sâu 2 → luận điểm chuyển sang khả năng biểu đạt; quorum R=2/W=1 chỉ đạt 93,5% read-your-writes; write sharding 10 shard trên 16 phân vùng vẫn còn lệch 3,2×; DynamoDB rẻ hơn Postgres tự vận hành ~12× ở 200k đơn/ngày với 77% hoá đơn là lưu trữ chứ không phải thông lượng; DuckDB ép kiểu im lặng khi làm phẳng JSON.

**Kèm `lab-starter/27-nosql/`**: docker-compose (redis 7 + mongo 7 + cassandra 4.1 + dynamodb-local), seed MongoDB, schema CQL, script boto3, README có mục "Khi hỏng thì soi gì". `lab-starter/README.md` cập nhật thành 4 lab.

Index cập nhật 27 masterclass; rebuild + mã hoá lại (0701), giải mã kiểm chứng khớp.

---

# Round 6 — 29/07/2026 (Masterclass 26 — Phân tích dữ liệu nâng cao)

**Mới: `26-advanced-analytics-masterclass.html`** (~485KB, 17 chương + quiz, ~64.700 từ, 40 dẫn nguồn). Định vị để không giẫm lên Masterclass 03 (metric nghiệp vụ) và 25 (data mining): khoá này là **suy diễn thống kê, thiết kế thực nghiệm, suy luận nhân quả và mô hình thống kê** — bộ công cụ trả lời câu hỏi *can thiệp*, khác với khai phá mẫu và dự báo.

Cấu trúc: (1) Định vị phân tích nâng cao, thang bậc nhân quả Pearl, estimand trước dữ liệu; (2) Phân phối mẫu, CLT, bootstrap/BCa, delta method, ratio metrics; (3) Kiểm định giả thuyết, bốn cách hiểu sai p-value, power và MDE, winner's curse; (4) A/B testing — SRM, CUPED, peeking, guardrail, vi phạm SUTVA; (5) Kết quả tiềm năng và DAG — confounder/mediator/collider, post-treatment bias; (6) Bán thực nghiệm — PSM/IPW/AIPW, DiD và vấn đề TWFE so le, synthetic control, RDD, IV; (7) Uplift và CATE — meta-learner, causal forest, đường Qini; (8) Hồi quy tuyến tính — Gauss–Markov, chẩn đoán, robust SE, hồi quy phân vị; (9) GLM — logistic/odds ratio vs marginal effect, Poisson quá tán, offset; (10) Dữ liệu phân cấp — ICC, fixed vs random effects, shrinkage; (11) Phân tích sống sót — Kaplan–Meier, Cox, kiểm tra PH, rủi ro cạnh tranh; (12) Chuỗi thời gian — tính dừng, SARIMA/ETS, MASE, backtesting, dự báo phân cấp; (13) Bayes ứng dụng — Beta–Binomial, A/B Bayes, partial pooling; (14) Đo lường marketing — attribution vs incrementality, geo experiment, MMM với adstock/saturation; (15) Bất định và truyền đạt kết quả; (16) Phân tích tái lập được; (17) Lab end-to-end + capstone; quiz 10 câu.

**Toàn bộ code chạy thật** (numpy/scipy/statsmodels/scikit-learn/lifelines/linearmodels); mọi dòng output được đối chiếu từng ký tự với log chạy — 100% khớp. Nhiều kết luận viết lại theo số liệu thực đo thay vì theo kỳ vọng: Student t-test có **hai** chế độ hỏng ngược nhau (α phồng lên 33,5% hoặc sụp về 0%); BCa chỉ cải thiện coverage từ 86,8% lên 88,7% chứ không sửa được; TWFE ước lượng thấp hơn ATT thật 61,3% khi can thiệp so le; S-learner thắng T-learner trên bộ dữ liệu này; Cox HR bị suy giảm do frailty và phân tầng không sửa được; quy tắc tổn thất kỳ vọng Bayes vẫn cho 34,8% dương tính giả khi nhìn lén; MMM ước lượng tự do có R² cao nhất nhưng sai ROI 96,2%.

Index cập nhật 26 masterclass; rebuild + mã hoá lại (0701), giải mã kiểm chứng khớp.

---

# Round 5 — 29/07/2026 (Masterclass 25 — Data Mining)

**Mới: `25-data-mining-masterclass.html`** (~445KB, 16 chương + quiz, ~57.000 từ) — module chuyên sâu về khai phá dữ liệu, viết theo văn phong học thuật ứng dụng (formal, không sáo ngữ), 52 dẫn nguồn gốc thuật toán.

Cấu trúc: (1) Định vị data mining trong KDD/CRISP-DM, phân biệt với thống kê suy diễn, ML và BI; (2) Kiểu thuộc tính, độ đo khoảng cách, chuẩn hoá, rời rạc hoá, lời nguyền số chiều; (3) Luật kết hợp — Apriori và FP-Growth, support/confidence/lift/leverage/conviction; (4) Mẫu tuần tự — GSP, PrefixSpan, ràng buộc gap; (5) Phân cụm — k-means/k-means++, hierarchical, DBSCAN/HDBSCAN, GMM-EM, chọn k và đánh giá; (6) Phân lớp cổ điển — cây quyết định, Naive Bayes, kNN, hồi quy logistic; (7) Ensemble — bagging/RF, gradient boosting, XGBoost/LightGBM/CatBoost, vì sao GBDT thắng trên dữ liệu bảng; (8) Đánh giá và hiệu chuẩn — CV đúng cách, PR-AUC vs ROC-AUC, calibration, ngưỡng theo chi phí; (9) Phát hiện bất thường — thống kê, Isolation Forest, LOF, đánh giá khi không có nhãn; (10) Đặc trưng và rò rỉ dữ liệu; (11) Dữ liệu mất cân bằng; (12) Diễn giải mô hình — permutation importance, SHAP, PDP/ALE; (13) Khai phá văn bản — TF-IDF, LDA/NMF, embeddings; (14) Khai phá ở quy mô lớn — lấy mẫu, HLL/CMS/MinHash-LSH, học tăng dần; (15) Cạm bẫy phương pháp luận — so sánh bội, p-hacking, Simpson, drift, công bằng thuật toán; (16) Lab end-to-end + capstone; quiz 10 câu tình huống.

**Toàn bộ code chạy thật** trong sandbox (scikit-learn 1.7, mlxtend, LightGBM 4.7, XGBoost 3.2, SHAP 0.49, datasketch, imbalanced-learn); output trong bài là output thật, seed cố định để tái lập. Nhiều kết luận được viết lại theo số liệu thực đo thay vì theo kỳ vọng lý thuyết, ví dụ: FP-Growth của mlxtend chậm hơn Apriori do khác biệt cài đặt (vector hoá NumPy vs đệ quy Python) — giữ nguyên và rút bài học về khoảng cách giữa độ phức tạp tiệm cận và thời gian chạy; SMOTE cải thiện xếp hạng ở mô hình này nhưng phá hiệu chuẩn ở mọi mô hình; silhouette xếp hạng ngược ARI trên dữ liệu hình vành khăn; rò rỉ qua `StandardScaler` thực tế gần bằng 0 trong khi rò rỉ thời gian +0,054 AUC.

Index cập nhật 25 masterclass, nhóm mới "Phân tích & Khai phá dữ liệu". Rebuild + mã hóa lại (make-protected nay có gzip: 7,9MB → 3,3MB), giải mã kiểm chứng khớp.

---

**Trạng thái cuối round 4:** rebuild + 2 bản mã hóa (0701) tạo lại, giải mã kiểm chứng khớp; các fix round 4 xác nhận có mặt trong bản gộp. Code đã chạy kiểm chứng thật đến nay: file 03, 05, 07 (SQL mới), 10, 12 (DAG parse), 15 (batch), 19, 21, 23. Không chạy được trong sandbox (cần Docker/cloud): lab compose 11/13, K8s manifests, code cloud-specific 14/15/20 — đã verify bằng docs + signature.

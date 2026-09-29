# Đánh giá bộ tài liệu tự học Data Engineering (23 masterclass)

Ngày đánh giá: 10/07/2026. Phương pháp: strip toàn bộ HTML sang text (~500.000 từ), trích xuất outline heading + thống kê code/bài tập cho từng file, sau đó 4 reviewer đọc sâu theo mẫu đại diện rộng (mỗi file 4-6 vùng ~400 dòng ở đầu/giữa/cuối, đọc kỹ toàn bộ code tìm được, một số đoạn code được **chạy thử thật** để kiểm chứng), đối chiếu với lộ trình DE chuẩn ngành giữa 2026 qua nghiên cứu web độc lập.

---

## 1. Kết luận tổng quan

**Điểm chung cả bộ: 7.5/10** — thuộc nhóm tài liệu tiếng Việt tốt nhất trong phân khúc tự học DE về mặt **tư duy và khái niệm**, nhưng có một khiếm khuyết hệ thống nghiêm trọng: **code không đáng tin**.

Ba mệnh đề quan trọng nhất, nói thẳng:

1. **Phần lý thuyết/khái niệm tin được ~85-90%.** Bộ tài liệu xây mô hình tư duy senior thật: internals (hint bits của PostgreSQL, Unified Memory eviction của Spark, position vs equality delete của Iceberg), trade-off hai chiều ở hầu hết quyết định, văn hóa "cạm bẫy production" dày đặc và phần lớn chính xác. 60/60 câu quiz được kiểm tra ngẫu nhiên đều có đáp án đúng.

2. **Phần code phải coi là pseudo-code (mã giả), tuyệt đối không copy-paste.** Đây là bộ tài liệu sinh bằng LLM chưa qua bước chạy thử — bằng chứng không thể chối: ký tự Trung Quốc lọt vào bảng cgroups (file 13), placeholder "scn" chưa thay (file 03), ghi chú tác giả lọt vào bài (file 05), API bịa hoàn toàn (`CREATE SEMANTIC MODEL` của Snowflake, `pip install cubejs`, `io.debezium.connector.postgresql.SourceConnector`...), tên model ngoại suy ("GPT-5.5", "DeepSeek V4"). Hơn 40 lỗi code cụ thể đã được xác nhận, nhiều lỗi nằm ngay trong "mẫu chuẩn" được dạy — nguy hiểm nhất là loại lỗi **sai âm thầm** (salting join trả NULL toàn bộ, `COUNT(DISTINCT customer_sk)` trên dim SCD2 đếm đôi).

3. **Đây là "sách đọc để hiểu cơ chế", không phải khóa thực hành**, dù tên là masterclass. Không có dataset, không repo, không docker-compose chạy được nguyên trạng (các lab E2E đều có lỗi chặn); output terminal là dàn dựng; bài tập "tự kiểm — không lời giải". Tỷ lệ lý thuyết/thực hành toàn bộ ~75/25, và phần 25% đó phần lớn là code minh họa để đọc.

Hệ quả thực tế cho cách dùng: **đọc để xây mental model thì rất tốt; kỹ năng tay nghề phải xây ở nơi khác** (mục 5).

---

## 2. Đánh giá theo tiêu chí

### 2.1. Độ bao phủ so với lộ trình DE chuẩn 2026

Đối chiếu với yêu cầu JD thực tế 2025-2026 (SQL + Python xuất hiện ~94% JD, dbt ~61%, Airflow ~58%; nguồn: phân tích JD của dataexpert.io, dataquest.io, khảo sát Joe Reis 2026):

**Bao phủ tốt:** Linux, PostgreSQL (xuất sắc), data modeling, pipeline patterns (idempotency, CDC, backfill, data contract), Spark (kèm Spark 4.0), Kafka/streaming (kèm KRaft, Flink), Airflow (có hẳn mục Airflow 3.0 — đúng và hiếm), Docker/K8s, AWS + GCP (đối xứng, học so sánh được), lakehouse/Iceberg (file 16 là file tốt nhất bộ), Snowflake/Databricks, DuckDB (kèm DuckLake 5/2025), Python engineering hiện đại (uv, ruff, Pydantic v2 — đầy đủ), GenAI/RAG cho DE, system design, platform engineering/CI-CD (mức khái niệm), và business domain — thứ gần như không tài liệu DE nào có.

**Lỗ hổng coverage, xếp theo mức nghiêm trọng:**

| Lỗ hổng | Mức độ | Ghi chú |
|---|---|---|
| **Không có masterclass dbt riêng** | Nặng nhất | dbt ~61% JD. Nội dung dbt rải trong file 04/06/07 ở mức fragment; lab dbt của file 07 không chạy được. Đây là kỹ năng "cặp đôi mặc định" với Airflow mà bộ tài liệu xem nhẹ nhất so với thị trường. |
| Airflow Datasets/Assets (data-aware scheduling) | Nặng | File 12 hoàn toàn không dạy, thậm chí bảng so sánh còn đánh giá thấp Airflow sai ở đúng điểm này. |
| Lakehouse vắng trong Data Modeling (file 06) | Trung bình | Model trên Iceberg/Delta (MERGE-on-read, partition evolution) khác model trên warehouse — file 06 bỏ qua hoàn toàn, may là file 16 bù được một phần. |
| Terraform/IaC hands-on | Trung bình | File 17 chỉ dạy khái niệm; JD mid-level yêu cầu dùng thật. |
| Git workflow / code review / CI-CD thực hành | Trung bình | Có lý thuyết ở 17, không có thực hành. |
| dbt Fusion, Kafka 4.0, GCP Managed Kafka | Nhẹ | Các chuyển động 2025 mà tài liệu trễ nhịp. |
| Azure | Nhẹ | Chấp nhận được với thị trường VN (AWS/GCP phổ biến hơn), nhưng nên biết là có lỗ hổng nếu nhắm enterprise. |

**Phần thừa:** trùng lặp nội bộ đáng kể. File 07 trùng ~50% với file 06 (dạy lại star schema/SCD nông hơn — chỉ nên đọc 07 từ phần semantic layer); series 08-11 lặp schema evolution/backward-compat ở 3 file, SSE dạy 3 lần (~15-20% series là lặp); file 02 module 22 trùng ~70% module 6-7 của chính nó; file 06 có khối "Lý thuyết mở rộng" lặp ~30% word count; file _19-mlops chương 12-14 chồng ~70% lên file 22. Tổng thể có thể cắt ~20% dung lượng mà không mất thông tin.

### 2.2. Độ sâu kỹ thuật

Không đồng đều nhưng nhìn chung cao hơn mặt bằng tutorial:

- **Nhóm sâu nhất (8-9/10):** 02 PostgreSQL (sâu nhất bộ — hint bits, HOT update, lock queue, plan cache), 16 Lakehouse (giải thích *cơ chế* chứ không liệt kê tính năng), 04 Pipeline, 06 Modeling, 11 Streaming (phần Flink chính xác và sâu hiếm thấy), 18 System Design (sâu về *phán đoán*, capstone có rubric), _19 MLOps, 01 Linux.
- **Nhóm khá (7-7.5/10):** 05 Spark, 08 WebAPI, 12 Airflow, 13 Docker/K8s, 14 AWS, 17 Platform, 20 Snowflake/Databricks, 22 GenAI, 03 Business.
- **Nhóm mỏng hơn (6-7/10):** 07, 09, 15 GCP, 19 DuckDB, 21 Python (chính xác nhất bộ nhưng chỉ ~9k từ — bằng 1/4 file 01, thiếu hẳn bài tập/capstone), 10 Data Quality (khái niệm ổn, mọi thứ khác tệ).

Đặc điểm: độ sâu là **độ sâu của pattern và cơ chế**, không phải độ sâu triển khai — không có tuning config thật, benchmark phần lớn là số minh họa (riêng file 05 trung thực dán nhãn "ví dụ minh họa", các file khác đôi khi trình bày như số đo thật).

### 2.3. Tính chính xác — danh sách lỗi tiêu biểu cần biết trước khi đọc

Khái niệm gần như sạch; lỗi tập trung ở code. Những lỗi đáng nhớ nhất (đầy đủ hơn nằm trong báo cáo chi tiết của từng nhóm):

**Loại "sai âm thầm" — nguy hiểm nhất:**
- File 05 (Spark): kỹ thuật salting chống skew dùng `col("customer_id") + lit("_") + col("salt")` — toán tử `+` trong Spark là cộng số học → **NULL toàn bộ, join sai hoàn toàn** (phải dùng `concat_ws`). Đây là kỹ thuật đinh của module chống skew.
- File 06 (Modeling): query mẫu trong case study `COUNT(DISTINCT f.customer_sk)` trên dim SCD2 → khách đổi tier giữa kỳ bị đếm đôi.
- File 12 (Airflow): Jinja `{{ ds }}` đặt trong string ở thân hàm Python — không được render → query luôn trả 0 dòng.
- File 04 (Pipeline): `spark.read.parquet(path)` rồi `write.mode("overwrite")` vào **cùng path** — nguy cơ mất dữ liệu, mâu thuẫn với chính lời dạy "atomic swap" của nó.

**Loại "API bịa" (hallucination):**
- File 20: `CREATE SEMANTIC MODEL`, hàm SQL `CORTEX.CORTEX_ANALYST(...)`, `CREATE VECTOR INDEX ... TYPE HNSW` của Databricks, Dynamic Table tự tham chiếu chính nó — đều không tồn tại. Chương internals 9-10 của file này là vùng nhiễm nặng nhất.
- File 07: gần toàn bộ code Cube.dev bịa (config keys, `ref()`, `pip install cubejs`, REST API format).
- File 10: Great Expectations trộn 3 thế hệ API trong một class + expectation không tồn tại; Pact API bịa. File này còn bị "loạn chữ" tiếng Việt hệ thống ("mọi người yên tím", "xảy ra bất chợp") — file duy nhất lỗi văn bản nặng.
- File 11: Debezium connector class sai (2 lần), aiokafka commit thủ công khi chưa tắt auto-commit, proto3 dùng `default` (cấm trong proto3), docker-compose Kafka hai listener cùng port.
- File 15: pipeline Beam có 4 lỗi API (`Timestampnow()`, `Repeat`, topic+subscription cùng lúc, `table_spec=`); DAG Composer import `TaskFlow` không tồn tại.
- File 19: pattern `duckdb.sql(sql, [params])` sai chữ ký (đã chạy thử, ra TypeError) lặp ở ít nhất 4 đoạn gồm cả capstone.

**Loại lỗi fact:**
- File 15: "GCP không có managed Kafka native" — sai, Google Cloud Managed Service for Apache Kafka GA từ cuối 2024.
- File 13: "cgroup v1 deprecated từ K8s 1.26" — sai (maintenance mode từ 1.31).
- File 06: Knight Capital 2012 bị kể sai bản chất; giới hạn partition Snowflake/BigQuery sai.
- File 08: đảo ngược khái niệm sync/async handler trong FastAPI — lỗi khái niệm hiếm hoi nhưng ở đúng chỗ dễ hiểu nhầm nhất.

**Quy luật rút ra:** code càng dài và càng thuộc hệ sinh thái có API đổi nhanh (Cube, GX, Pact, Databricks/Snowflake AI features) thì tỷ lệ bịa càng cao. CLI ngắn, SQL thuần và khái niệm thì đáng tin. Mức tin cậy code theo file, giảm dần: 21 > 08 > 16 > 22 ≈ _19 > 01/02/05/06 > 12/13/14 > 09/19 > 15 > 07 > 20 (chương internals) > 10.

### 2.4. Tính cập nhật (mốc giữa 2026)

Tổng thể là **ảnh chụp cuối 2024 - giữa 2025, dán nhãn 2026** — đạt yêu cầu nhưng trễ nửa nhịp:

- **Điểm cộng thật:** PostgreSQL 18, Spark 4.0, Airflow 3.0 (file 12), Iceberg spec v3 + REST Catalog + Polaris, Delta 4.0, Hudi 1.0, S3 Tables, DuckLake (5/2025), uv/ruff/Pydantic v2, Unity Catalog open-source, MCP. Nhiều file có mục "chuyển động 2024-2025" riêng và biết tự khai giới hạn thời điểm — trưởng thành.
- **Điểm trễ:** file 04 chưa biết Airflow 3 (viết bằng ngôn ngữ 2.x); version pin đời 2024 (duckdb 1.1.3, kind v1.29, Airflow image 2.10, EMR 6.15, ruff-pre-commit 0.5.0); file 22 dùng tên model ngoại suy sẽ lỗi thời trong 6-12 tháng (nhưng ~80% nội dung file đó là nguyên lý chống-lỗi-thời có ý thức).

### 2.5. Tỷ lệ lý thuyết vs thực hành

~75/25 toàn bộ. Phân bố: thực hành nhiều nhất ở 13 (lab E2E nguyên module, ~45%), 08 (lab CRUD gần chạy được nguyên trạng — lab tốt nhất bộ), 01/02 (mật độ lệnh cao); ít nhất ở 03 (~90/10, chỉ ~4 khối SQL thật), 22, 18 (nhưng 18 bù bằng capstone thiết kế có rubric — đúng thể loại). Vấn đề không phải số lượng code mà là **không có scaffolding**: zero dataset, zero seed script, zero repo. Người học không thể "làm theo từ dòng 1" ở bất kỳ file nào.

---

## 3. Điểm mạnh / điểm yếu tổng hợp

**Điểm mạnh:**
1. Tư duy senior nhất quán: biết từ chối công cụ ("DuckDB trên laptop nhanh hơn cluster nhỏ", "đừng vội bỏ Airflow", "khi nào KHÔNG cần Data Mesh/LLM/Spark"), luôn nói về chi phí và trade-off. Đây là thứ tutorial thương mại hiếm khi dạy.
2. Thiết kế chương trình có chủ đích: cross-reference giữa 22 module dày và **chính xác** (đã kiểm tra ngẫu nhiên), cặp AWS/GCP đối xứng để học so sánh, "sợi chỉ đỏ" mỗi khóa được khép vòng.
3. Văn hóa cạm bẫy production: silent failure, exit 137, replication slot đầy đĩa, VACUUM xóa file của writer đang chạy, GDPR crypto-shredding... — gom đủ những thứ thường phải trả giá bằng sự cố thật mới học được.
4. Tiếng Việt chuyên nghiệp, thuật ngữ Anh giữ nguyên có giải nghĩa, ví dụ bản địa hóa (VND, fintech VN, Asia/Ho_Chi_Minh). Capstone file 18 dùng đúng domain "công ty sản xuất & trading" — khớp trực tiếp với bối cảnh Stavian.
5. Business domain (file 03) + MLOps (_19) là hai mảng gần như không bộ tài liệu DE nào có, và file _19 thực chất thuộc nhóm tốt nhất bộ (8/10) — nên đưa lại vào lộ trình làm phụ lục thay vì để mồ côi.

**Điểm yếu:**
1. Code sinh máy không chạy thử (mục 2.3) — khiếm khuyết lớn nhất, và nghịch lý là nó nặng nhất ở chính các file "tool" nơi người học cần copy code nhất.
2. Không có lab tái lập được — "masterclass" nhưng là sách đọc.
3. Trùng lặp ~20% và dấu vết biên tập dở dang (file 10 loạn chữ, module ghép sau "Tổng kết", đánh số lệch "Hết module 20" trong file 19).
4. Thiếu dbt như một trụ riêng — lệch pha rõ nhất so với JD thị trường.
5. Dung lượng hụt hơi ở cuối lộ trình: file 19-22 chỉ bằng 1/3 file 01-06; file 21 thiếu hẳn tầng luyện tập.

---

## 4. Những gì tài liệu KHÔNG THỂ cho bạn — và cách bù

Kể cả khi mọi lỗi code được sửa, một bộ tài liệu đọc không tạo ra được những thứ sau — và nhà tuyển dụng phỏng vấn mid-level sẽ hỏi đúng vào đây:

1. **Kinh nghiệm hệ thống chạy thật và hỏng thật.** Tài liệu mô tả sự cố ("2h sáng pipeline chết") nhưng bạn chưa từng tự tay debug một DAG treo, một consumer lag tăng, một warehouse bill nổ. → **Bù:** tự dựng pipeline chạy **hằng ngày trong nhiều tuần** trên schedule thật (VPS rẻ hoặc free tier), để nó hỏng, và tự sửa. Một pipeline chạy 60 ngày dạy nhiều hơn 60 giờ đọc.
2. **Dữ liệu bẩn quy mô thật.** Mọi ví dụ trong tài liệu đều là dữ liệu sạch giả định. → **Bù:** đây là lợi thế lớn nhất của bạn — **dữ liệu kinh doanh tại Stavian**. Đề xuất một dự án nội bộ: pipeline tự động hóa báo cáo bạn đang làm tay (nguồn → staging → dbt model → dashboard Power BI), chạy bằng Airflow. Vừa là portfolio, vừa là giá trị thật cho công ty, vừa khớp luôn đề capstone file 18.
3. **CI/CD và làm việc nhóm trên code.** → **Bù:** mọi dự án cá nhân đều qua GitHub + pull request cho chính mình + GitHub Actions chạy `ruff` + `pytest` + `dbt build`. Làm **DataTalksClub DE Zoomcamp** (miễn phí, cohort tháng 1 hằng năm, có peer review) — nó chính là mảnh scaffolding mà bộ tài liệu này thiếu: Docker, Terraform, GCP, dbt, BigQuery, Spark, Kafka + final project được chấm.
4. **On-call và vận hành.** Không bù được hoàn toàn khi chưa đi làm chính thức, nhưng có thể mô phỏng: gắn alert (Slack webhook) vào pipeline cá nhân, viết postmortem (biên bản sự cố) cho mỗi lần hỏng — file 17/18 dạy đúng format.
5. **Chứng chỉ** (theo phân tích 1.000+ JD 2026: 1 cert cloud + portfolio là điểm ngọt, cert không thay được project):
   - Ưu tiên 1: **AWS Certified Data Engineer – Associate** ($150) hoặc **GCP Professional Data Engineer** ($200) — chọn theo cloud bạn học kỹ ở mục 5.
   - Ưu tiên 2 (nếu đi hướng Spark/lakehouse): **Databricks Data Engineer Associate** ($200).
   - SnowPro chỉ đáng nếu công ty dùng Snowflake. Cert Airflow của Astronomer rẻ, nhận diện hẹp, để sau.
6. **Sách bù chiều sâu:** *Fundamentals of Data Engineering* (Reis & Housley) đọc song song giai đoạn 1-2; *Designing Data-Intensive Applications 2nd edition* (đã ra ~2/2026) đọc sau khi xong file 18.

---

## 5. Lộ trình học đề xuất cho Vinh

Xuất phát điểm: SQL/Python khá, nền business-tài chính tốt (→ file 03 phần lớn là ôn), chưa có nền hệ thống (Linux, Docker, distributed). Nguyên tắc xuyên suốt: **mỗi tuần phải có ít nhất một thứ tự tay dựng lại được** — vì tài liệu không cho bạn điều đó; và **mọi code block >5 dòng trong tài liệu phải được kiểm chứng lại bằng docs chính thức hoặc chạy thử** (dùng Cursor/Claude để đối chiếu nhanh — chính các lỗi liệt kê ở mục 2.3 là bài tập review code tốt).

### Giai đoạn 0 — Nền hệ thống (4-6 tuần)
- **01 Linux — học KỸ** module 1-12 (thực dụng) + case study; lượt đầu chỉ lướt phần internals 13-19, quay lại sau giai đoạn 2. Thực hành trên WSL2/VM thật, không đọc chay.
- **02 PostgreSQL — học KỸ toàn bộ** (file tốt nhất bộ; bỏ module 22 vì trùng 6-7). Dựng Postgres bằng Docker, tự sinh 10M dòng bằng `generate_series` và ĐO bằng `EXPLAIN (ANALYZE, BUFFERS)` như bài tập của nó yêu cầu.
- **21 Python SWE — đọc KỸ** (ngắn, chính xác nhất bộ): chuyển toàn bộ workflow cá nhân sang uv + ruff + pytest ngay từ tuần này.
- 03 Business — **lướt** (bạn có nền tốt hơn tài liệu ở mảng tài chính-kế toán); chỉ đọc kỹ module DDD→data model (bảng ánh xạ Aggregate→fact/dim là thứ đáng giá) và cụm module ngân hàng nếu tò mò. Lưu ý lỗi DAU/MAU của nó.

### Giai đoạn 1 — Core DE (6-8 tuần) ⭐ quan trọng nhất
- **04 Data Pipeline — học KỸ** (file khung xương của cả bộ). Tự bổ sung: đọc release notes Airflow 3.
- **06 Data Modeling — học KỸ**, bỏ qua các khối "Lý thuyết mở rộng" (lặp); cảnh giác DDL trộn dialect. Làm bài 30 ngày của nó với Jaffle Shop/NYC Taxi — bài tập tốt nhất bộ.
- **12 Airflow — học KỸ** + tự học **Assets/data-aware scheduling** từ docs chính thức (tài liệu thiếu hẳn). Lab E2E của nó hỏng — coi như bài tập: tự dựng lại DAG đó cho chạy được.
- **dbt — học NGOÀI bộ tài liệu:** làm official dbt tutorial + Jaffle Shop, rồi mới đọc file 07 **từ phần semantic layer trở đi** (nửa đầu trùng file 06; code Cube.dev của nó bịa — chỉ đọc concept).
- Song song: **bắt đầu dự án portfolio #1** — pipeline dữ liệu Stavian hoặc dữ liệu công khai (giá giấy/commodity, xuất nhập khẩu VN): ingest → Postgres → dbt → dashboard, chạy Airflow hằng ngày, GitHub + CI.

### Giai đoạn 2 — Scale & Streaming (6-8 tuần)
- **05 Spark — học KỸ** phần tư duy shuffle/Catalyst/skew/AQE; nhớ lỗi salting và Delta `outputMode("update")` khi đọc. Thực hành bằng `pip install pyspark` local với dataset tự tạo vài GB.
- **16 Lakehouse — học KỸ toàn bộ** (file chính xác và cập nhật nhất bộ; 4 bài tập của nó có tiêu chí tự kiểm chứng — làm hết).
- **11 Streaming — học KỸ** lý thuyết (commit semantics, watermark, Flink — phần chuẩn nhất); lab CDC của nó hỏng ở 3 chỗ (compose, connector class, RLS) — tự sửa là bài học đắt giá. 08 đọc kỹ nếu định làm data API; 09 đọc chọn lọc (cursor pagination + caching — 2 chương hiếm có tiếng Việt); **10 chỉ đọc khái niệm data contract, bỏ toàn bộ code** (GX/Pact bịa nặng), học Great Expectations/Soda từ docs chính thức.
- **19 DuckDB — lướt nhanh** (nửa ngày), dùng DuckDB làm workbench cá nhân từ đây.

### Giai đoạn 3 — Cloud & Platform (4-6 tuần)
- **Chọn MỘT cloud học kỹ, một cái lướt.** Gợi ý cho bối cảnh VN: **15 GCP kỹ** (BigQuery phổ biến ở VN, free tier hào phóng, và cert GCP PDE giá trị cao) hoặc 14 AWS nếu Stavian/công ty mục tiêu dùng AWS. Lưu ý: code Beam/Composer của file 15 nhiều lỗi nhất bộ — concept đọc được, code làm theo docs.
- **13 Docker/K8s:** Docker học kỹ (bắt buộc), K8s hiểu khái niệm là đủ ở mức junior→mid.
- **20 Snowflake/Databricks — đọc hiểu** chương 1-7 (vận hành + chi phí, tốt); **chương internals 9-10 đọc với thái độ nghi ngờ** (vùng hallucination nặng nhất bộ).
- **17 Platform — đọc** (khung control loop là insight đáng giá); Terraform học thực hành ngoài qua Zoomcamp.
- Thi **cert cloud** cuối giai đoạn này.

### Giai đoạn 4 — Tổng hợp (3-4 tuần + dài hạn)
- **18 System Design — học KỸ và LÀM CAPSTONE** (đề "Data Platform cho công ty sản xuất & trading" — chính là Stavian; làm đủ 4 mức nộp, mức 2+ dùng dự án portfolio đã có). Đọc kèm DDIA 2nd edition.
- **22 GenAI — đọc** (nguyên lý tốt, bỏ qua bảng tên model); **_19 MLOps — đọc** như phụ lục (chất lượng 8/10, đặc biệt phù hợp vì nó viết cho người có nền finance; bỏ chương 12-14 vì trùng file 22).
- Tham gia **DE Zoomcamp cohort tháng 1/2027** để có project được chấm điểm + peer review — lấp đúng lỗ scaffolding.

**Tổng thời gian: ~6-9 tháng** song song với thực tập. Đến giữa 2027: nền khái niệm từ bộ tài liệu này + 2 dự án end-to-end chạy thật + 1 cert cloud + kinh nghiệm dữ liệu thật tại Stavian — đủ hồ sơ ứng tuyển DE junior mạnh hoặc mid ở công ty vừa.

---

## 6. Nếu muốn sửa bộ tài liệu (ưu tiên giảm dần)

1. Chạy thử và sửa mọi code block >10 dòng — bắt đầu từ file 10 (viết lại), 20 (chương 9-10), 07 (Cube), 15 (Beam/Composer), 19 (params), 11 (Kafka client), 12 (lab), 05 (salting).
2. Viết thêm một masterclass dbt đúng nghĩa + bổ sung Assets vào file 12.
3. Thêm scaffolding: 1 repo GitHub với docker-compose + dataset + seed script dùng chung cho cả bộ.
4. Khử trùng lặp (07 nửa đầu, 02 module 22, khối "Lý thuyết mở rộng" file 06) và sửa lỗi văn bản file 10.
5. Đưa _19-mlops vào index làm phụ lục chính thức; refresh version pin (duckdb, kind, Airflow image, EMR).

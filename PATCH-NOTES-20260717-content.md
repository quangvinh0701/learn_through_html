# Patch Notes — 17/07/2026 (đợt 3: bổ sung nội dung cho các file yếu)

Backup nguyên trạng: `_backup-before-content-20260717/` (06, 10, 19, 21).

Nguyên tắc của đợt này — sửa đúng cái bệnh cũ của bộ tài liệu: **mọi snippet trong module mới đều được chạy thật trong sandbox trước khi vào bài** (duckdb 1.5.4, pandera 0.32, tenacity 9.1, pydantic 2.13, Python 3.10, Linux 2 vCPU). Output/số đo trong bài dán nguyên từ terminal, có ghi chú môi trường. Không có code cloud bịa.

## Tổng quan

| File | Trước | Sau | Thêm |
|---|---|---|---|
| 19 DuckDB | 19 tab · 9.979 từ (~45p) | 23 tab · 14.544 từ (~66p) | +4 module, +46% nội dung |
| 10 Data Quality | 14 tab · 15.986 từ | 17 tab · 19.212 từ (~87p) | +3 module |
| 21 Python SWE | 10 tab · 15.206 từ | 12 tab · 16.997 từ (~77p) | +2 module |
| 06 Data Modeling | 22 tab · 27.093 từ | 23 tab · 28.127 từ | +1 module |

Tổng bộ: ~40 giờ đọc. Khoảng +10.600 từ mới, 10 module.

## File 19 — DuckDB (mỏng nhất bộ → đã dày lên đáng kể)

- **M20 Storage & Pushdown**: 3 tầng cắt I/O; đo thật projection pushdown (0,39s vs 0,73s trên 5M dòng), zone map sorted vs unsorted (**0,031s vs 0,247s — 8x**), cách đọc EXPLAIN ANALYZE (cây thật), native .duckdb vs Parquet trần.
- **M21 Out-of-core**: bộ ba memory_limit/temp_directory/preserve_insertion_order; demo thật ORDER BY 6M dòng dưới trần 200MB (7,4s, không OOM); PARTITION_BY/hive_partitioning/filename/union_by_name (đều chạy thật); checklist 6 bước khi OOM.
- **M22 Python Ecosystem**: breaking change 1.5 `.arrow()` → RecordBatchReader (bắt được nhờ chạy thật, kèm `to_arrow_table()`); replacement scan, relation API lazy, UDF (kèm thứ tự ưu tiên builtin→CASE→UDF), params ?/$, ATTACH staging pattern.
- **M23 Bài tập & Capstone**: 6 bài có lời giải gấp; capstone pipeline ngành giấy 3M dòng chạy thật end-to-end (raw bẩn → clean loại 11.760 dòng → star → MA3/ABC/QUALIFY → export 24 partition) + rubric 5 tiêu chí.
- Nav: 4 tab mới chèn trước Cheatsheet; Cheatsheet đánh số lại 24.

## File 10 — Data Quality (nông → có tầng thực chiến + vận hành)

- **M15 Quality Gates thực chiến**: bộ 6 SQL assertion theo quy ước "đếm vi phạm" (chạy thật trên 100k dòng gieo lỗi — bắt đúng 4/4 loại lỗi gieo); anomaly z-score theo window 7 ngày (demo bắt ngày sụt 73%, z=−45,4) kèm 2 bẫy (mùa vụ, baseline nhiễm outlier); Pandera 0.32 (`import pandera.pandas`, lazy=True, failure_cases); dbt tests; bản đồ chọn tầng — GX đứng cuối, không phải đầu.
- **M16 Vận hành**: SLI/SLO/SLA cho data + error budget; phân loại alert P1/P2/P3 chống alert fatigue; runbook incident 6 bước (kèm phân bố nguyên nhân thực tế); scorecard TTD/TTR; kinh tế học chất lượng — dám không check bảng phụ.
- **M17 Bài tập & Case study ngành**: 5 bài (thiết kế gate cho feed giá bột giấy, hard/soft, mùa vụ, reconciliation với kế toán 4 bước, viết SLO thật); 2 case study mổ xẻ: feed giá sai đơn vị USD/tấn→USD/kg (9 ngày mới phát hiện), backfill nguồn âm thầm đổi số kỳ đã chốt (data closing + bitemporal).

## File 21 — Python SWE (thiếu mảng resilience → đã có)

- **M09 Resilience**: cây exception transient/permanent; tenacity đúng API (retry_if_exception_type, wait_exponential_jitter, reraise — demo thật retry 2 lần rồi thành công, permanent fail ngay sau 1 lần gọi); retry chỉ đặt lên hàm idempotent; httpx timeout tách connect/read; circuit breaker 15 dòng chạy thật (['thất','thất','thất','FAST-FAIL'×3]).
- **M10 Pydantic v2 thực chiến**: model dòng đơn hàng với ràng buộc nghiệp vụ (demo lỗi gom theo field); TypeAdapter đo thật 50k dòng/0,92s + ranh giới "validate tại biên, trong warehouse để SQL lo"; pydantic-settings 12-factor (env ETL_* — chạy thật); data contract bằng model chung + JSON Schema; bản đồ Pydantic/Pandera/dbt tests.
- Capstone/Quiz đánh số lại 11/12.

## File 06 — Data Modeling (+M22 Modeling trên Lakehouse)

Lấp gap review nêu: điều không đổi (star/grain/SCD); 4 luật đổi — UPDATE đắt (CoW/MoR → snapshot dimension cho dim đổi nhiều, bẫy MERGE 5 phút), không index (partition + sort lúc ghi, partition evolution), surrogate key không SEQUENCE (hash key deterministic, tránh UUID), time travel ≠ SCD (retention); checklist 6 câu trước CREATE TABLE. Trỏ chéo sang khoá 16 cho phần cơ chế. Quiz đánh số lại 23.

## Shell (build.py template)

- Thêm `tabIdOf()` — hỗ trợ cả `data-tab` lẫn `data-target` (chỉ file 19 dùng data-target; trước đây bộ đếm module M x/y, viewed tracking và dropdown không hoạt động với file 19).

## Verify

- Tag balance (section/div/details) pass cả 4 file sau chèn; node --check shell pass; jsdom smoke pass (24 bài/14 nhóm); round-trip mã hóa 0701 + gunzip khớp MD5; index.html ~3,0MB.
- Code không chạy thử được trong sandbox (dbt schema.yml, httpx client) được dán nhãn rõ trong bài và viết theo cú pháp docs chuẩn, phạm vi tối thiểu.

---

# Đợt 4 — 18/07/2026: File 17 +2 module Git & CI/CD thực hành

Lấp gap "Git workflow / code review / CI-CD thực hành" (mức Trung bình trong DANH-GIA, chưa ai vá). Chọn theo nghiên cứu thị trường 2026 + quyết định của chủ tài liệu (bỏ qua ClickHouse/Fabric/Forecasting đợt này). Backup file 17 đã thêm vào `_backup-before-content-20260717/`.

- **M17 Git cho Data Team** (t18, ~980 từ): .gitignore chuẩn repo data (secrets/artifacts); trunk-based + Conventional Commits; **demo conflict SQL thật end-to-end** (markers → resolve giữ cả 2 cột → graph log, output dán nguyên văn); PR review checklist 8 điểm cho SQL/pipeline (grain, downstream, incremental, test, cost, idempotent, backfill, PII); pre-commit với hook sqlfluff+ruff — config + kết quả chạy thật (Passed).
- **M18 CI/CD Pipeline dữ liệu** (t19, ~1.090 từ): tháp test 5 tầng cho data (static→unit→contract→data test→smoke) và bệnh nhầm tầng; **unit test SQL bằng DuckDB in-memory — 3 test chạy thật** (kèm chi tiết bắt được nhờ chạy thử: executemany không nhận list rỗng); sqlfluff lint/fix before-after thật (7 vi phạm → file sạch); workflow GitHub Actions hoàn chỉnh 3 job (lint+unit / slim CI `state:modified+ --defer` cho PR / build prod từ main với environment+secrets — dán nhãn "bám docs, không chạy thử được trong sandbox"); promote/rollback bằng git revert nhờ idempotent; lộ trình CI tối thiểu cho team 2 người.
- Cheatsheet file 17 đánh số lại 19. File 17: 17→19 tab, 12.924→15.007 từ (~68 phút).
- Verify: tag balance pass, bundle == file nguồn byte-identical, round-trip 0701 cả 2 bản mã hóa OK.
- Công cụ chạy thật đợt này: git 2.x, pre-commit 4.6, sqlfluff 4.2, ruff 0.15, pytest, duckdb 1.5.4.

---

# Đợt 5 — 18/07/2026: File 18 +2 module "Xử lý dữ liệu lớn"

Theo yêu cầu hiểu sâu các cách xử lý dữ liệu lớn. Đặt vào file 18 System Design (nơi hợp nhất — file trước đó có 0 dòng về DuckDB/Polars/chọn engine, chỉ 2 lần nhắc shuffle). Backup file 18 trong `_backup-before-content-20260717/`.

- **M17 Bản đồ Xử lý Dữ liệu lớn** (t19, ~1.220 từ): ba thời kỳ (MapReduce → cloud MPP → single-node renaissance, kèm luận điểm "big data is dead" và lý do vật lý của đảo chiều); 4 họ engine với khế ước đánh đổi riêng (single-node vectorized / MPP warehouse / Spark / streaming stateful — mỗi họ trỏ về khoá dạy sâu tương ứng 19/20/05/11); 3 cơ chế xuyên suốt cần hiểu sâu: partitioning (đơn vị song song), shuffle (thuế của phân tán — vì sao network là ranh giới), columnar+vectorization và composable stack (Arrow/DataFusion/Velox); bảng so sánh 4 họ theo 7 tiêu chí.
- **M18 Chọn Engine 2026** (t20, ~1.310 từ): **benchmark chạy thật** cùng workload 5M dòng (filter+join+groupby, 2 vCPU): pandas 2,72s · polars 0,61s · duckdb 0,24s — kèm giải thích cơ chế từng mức chênh (eager vs lazy vs pushdown+pipeline); Spark local không cài kịp trong sandbox — ghi chú trung thực trong bài, điểm gãy thị trường lấy từ khảo sát ngành 2026 (single-node thắng tới ~100GB, rẻ hơn ~5x); cây quyết định 4 trục (working set thật — không phải kích thước kho, latency/concurrency, loại logic, chi phí vận hành); con đường tăng trưởng 4 bậc (scale-up → partition-parallel → warehouse serving → Spark) với nguyên tắc "lên khi đau thật"; 4 anti-pattern đốt tiền; bài tập xếp 5 workload có lời giải.
- File 18: 18→20 tab, 16.316→18.913 từ (~86 phút). Capstone/Cheatsheet đánh số lại 19/20.
- Verify: tag balance pass, bundle == disk, round-trip 0701 OK cả 2 bản. Tổng bộ giữ ~40 giờ đọc.
- Nguồn nghiên cứu: khảo sát so sánh engine 2026 (sparkingscala, onehouse, endjin benchmark Fabric, pola.rs, vutr.substack).

---

# Đợt 6 — 18/07/2026: Nâng cấp 5 file đầu (+5 module thực chiến, ~6.200 từ)

Nguyên tắc chọn nội dung: 5 file đầu vốn dày và điểm cao — không bơm chữ, chỉ lấp đúng hai thứ review chê cả bộ: **thiếu số đo thật** và **thiếu quy trình thực chiến**. Backup 5 file trong `_backup-before-content-20260717/`.

- **01 Linux +M23 "Chẩn đoán 60 giây"** (chạy thật toàn bộ): quy trình 6 lệnh USE-style; đọc load average theo số core; free -m (bẫy free vs available — số thật 1232 vs 3472MB); thí nghiệm thật đốt 2 core quan sát vmstat r=2/us=100; cây quyết định 10 giây từ vmstat; dd đo 117MB/s; truy án OOM killer (dmesg, exit 137/cgroup).
- **02 PostgreSQL +M24 "Playbook chẩn đoán chậm production"** (SQL theo docs, dán nhãn không chạy thử được vì sandbox không có PG): rẽ nhánh 3 loại "chậm"; pg_stat_activity đọc 3 cột chẩn đoán (idle in transaction!); trình tự EXPLAIN 4 bước có kỷ luật (thống kê trước, index sau); pg_stat_statements chọn query đáng sửa theo total_time; bloat/autovacuum; cây blocking pg_blocking_pids; checkpoint gai I/O; bảng triệu chứng→nhánh; 3 bài tập dựng án thật. Kèm **box định hướng ở t22** (module trùng ~70% với 6-7 theo review — ghi thẳng cho người học biết cách đọc).
- **03 Business +M24 "Sản xuất & Trading hàng hoá"** (domain 0% coverage trước đó, đúng ngành chủ tài liệu): hai cỗ máy tiền nhà máy vs bàn trading; 5 khái niệm tiền nhà máy (fixed/variable + utilization, yield, OEE nhân 3 thừa số, standard vs actual cost, vòng tiền DIO/DSO/DPO); 4 khái niệm trading (basis vs chỉ số, position + mark-to-market snapshot, hedging ý thức vị thế, pass-through lag); bộ khung 8 bảng ánh xạ data model + 3 quyết định modeling định mệnh (snapshot vs transaction, đơn vị gốc, giá + tỷ giá gốc); 5 bẫy dữ liệu đặc sản; bài tập trên chính công ty người học.
- **04 Pipeline +M24 "Ingestion từ thế giới bừa bộn"** (chạy thật phần parse): Excel 6 lớp phòng thủ (file dựng đúng bệnh: merge cell, header dòng 4, dòng TỔNG, số kiểu VN 515,50 — parse thật ra 3 dòng sạch + 1 quarantine); CSV đoán encoding có kỷ luật (demo thật utf-8 fail → cp1258 → Sniffer ra ';'); watermark theo FILE với bảng manifest hash-là-căn-cước + 3 luật duplicate/bản sửa/đến muộn; SFTP (file đang ghi dở, đuôi .tmp→rename atomic) + email (inbox riêng cho máy, raw zone trước parse); "hợp đồng file" với con người + phản hồi tự động; ranh giới nới lỏng có chủ đích.
- **05 Spark +M23 "Tuning workbook"** (dán nhãn: cấu hình theo docs 3.5/4.0, sandbox không chạy được cluster): 5 con số Spark UI đọc trước tiên (max vs median = skew, spill, GC%); 3 công thức sizing thuộc lòng (shuffle partitions ≈ data/128MB với ví dụ 200GB→1600; tháp bộ nhớ executor + vì sao UDF Python tăng memoryOverhead chứ không phải heap; 4-5 core/executor); bộ cờ AQE và giới hạn của nó; bảng triệu chứng→thuốc 7 dòng; quy trình 5 bước chống "vặn loạn núm"; lời nhắc tuning lớn nhất nằm ngoài config (đọc ít hơn trước — nối khoá 18).
- Kết quả: 01: 23 tab/~173p · 02: 24 tab/~155p · 03: 24 tab/~234p · 04: 24 tab/~161p · 05: 23 tab/~183p. Tổng bộ ~41 giờ / 535.837 từ. Round-trip 0701 cả 2 bản OK, bundle == disk cả 5 file.
- Môi trường chạy thật đợt này: vmstat/free/dd/ps (Linux), pandas 2.x + openpyxl (Excel/CSV), csv.Sniffer. Đã thử cài pgserver và pyspark trong sandbox để đo thật cho 02/05 — không thành (mạng chặn/tải quá chậm), hai module đó dùng nhãn "bám docs" đúng quy ước.

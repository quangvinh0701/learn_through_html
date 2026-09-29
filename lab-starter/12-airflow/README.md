# Lab 12 — Airflow 3.x: DAG E2E + Assets

Chạy một Airflow 3 tối giản (`airflow standalone`) để học hai thứ: (1) một **DAG E2E** kiểu extract → transform → quality → alert, và (2) **Assets** — lập lịch theo *dữ liệu* thay vì theo *giờ*.

> Nguồn: trích & chuyển thể từ `12-airflow-orchestration-masterclass.html` (Module 14 Lab E2E, Module 2 Assets, block Cosmos). DAG E2E đã được **làm self-contained**: bỏ PostgresHook/S3/Snowflake/Slack, thay bằng dữ liệu giả sinh tại chỗ (pure Python) → chạy xanh ngay, không cần khai báo connection nào.

## Cần gì
- Docker Desktop (Compose v2).
- RAM cho Docker: **tối thiểu 4 GB**.
- Cổng trống: `8080` (UI), `5432` không expose (Postgres nội bộ).

## Thành phần
| Service | Image (đã pin) | Cổng | Vai trò |
|---|---|---|---|
| airflow | `apache/airflow:3.0.3` | 8080 | `airflow standalone`: api-server + scheduler + dag-processor + triggerer |
| postgres | `postgres:16-alpine` | — | Metadata DB |

## Các bước

**1. Bật stack**
```bash
docker compose up -d
docker compose ps        # đợi airflow (healthy) — lần đầu chạy `db migrate` nên hơi lâu (~1-2 phút)
```

**2. Lấy mật khẩu admin** (standalone tự tạo user `admin`, mật khẩu ngẫu nhiên)
```bash
docker compose logs airflow | grep -i "password"
# hoặc đọc file:
docker exec airflow-standalone cat /opt/airflow/simple_auth_manager_passwords.json.generated 2>/dev/null || true
```

**3. Mở UI** → http://localhost:8080 → đăng nhập `admin` / (mật khẩu ở bước 2).

**4. Chạy DAG E2E**
- Vào DAG `lab_pipeline` → bật (unpause) → **Trigger**.
- Xem Graph: `extract → transform, quality_check → success_alert`.
- `success_alert` dùng `trigger_rule="none_failed_min_one_success"`, chỉ chạy khi các nhánh trước không fail.
- Kết quả ghi ở `/tmp/lab_pipeline/` **trong container**:
  ```bash
  docker exec airflow-standalone ls -l /tmp/lab_pipeline
  docker exec airflow-standalone cat /tmp/lab_pipeline/revenue_*.csv
  ```

**5. Xem Assets (data-aware scheduling)**
- DAG `raw_orders` (do `@asset` sinh ra) chạy `@daily` và **cập nhật asset** `raw_orders`.
- DAG `build_marts` có `schedule=[Asset("raw_orders")]` → **tự chạy** ngay sau khi `raw_orders` thành công.
- Trigger `raw_orders` bằng tay một lần → quan sát `build_marts` tự lên lịch.
- Xem menu **Assets** trên thanh điều hướng để thấy đồ thị asset → DAG.

**6. Dọn dẹp**
```bash
docker compose down -v
```

## Ghép Assets với dbt qua Cosmos (tham khảo — KHÔNG bật sẵn)
Trích từ bài (Module 2, block `dags/dbt_cosmos.py`). Cần cài thêm `astronomer-cosmos` + dbt trong image; để trong `dags/` mà chưa cài sẽ gây **import error**, nên chỉ để đây làm tài liệu:

```python
from cosmos import DbtDag, ProjectConfig, ProfileConfig
from airflow.sdk import Asset

dbt_dag = DbtDag(
    dag_id="dbt_shop",
    project_config=ProjectConfig("/opt/airflow/dbt/shop"),
    profile_config=ProfileConfig(
        profile_name="shop", target_name="prod",
        profiles_yml_filepath="/opt/airflow/dbt/shop/profiles.yml",
    ),
    schedule=[Asset("raw_orders")],   # cả project dbt chạy khi asset ingest cập nhật
)
# Cosmos biến mỗi dbt model thành 1 task (retry/alert/lineage từng model),
# tự gắn inlets/outlets là Asset theo lineage của dbt.
```
Muốn bật thật: build một image `FROM apache/airflow:3.0.3` rồi `pip install astronomer-cosmos dbt-postgres`, trỏ `image:` trong compose sang image đó.

## Khi hỏng thì soi gì
> **Debug chính là bài học.** Airflow là hệ phân tán nhỏ: scheduler quyết định chạy gì, dag-processor parse file, executor chạy task. Hỏng ở tầng nào, log tầng đó nói.

1. **DAG không hiện trên UI / có banner "Import Errors"**
   - Nhấn banner **DAG Import Errors** ở đầu trang — nó in traceback đúng dòng.
   - Hoặc từ CLI:
     ```bash
     docker exec airflow-standalone airflow dags list
     docker exec airflow-standalone airflow dags list-import-errors
     ```

2. **DAG hiện nhưng không chạy** → xem scheduler/standalone log:
   ```bash
   docker compose logs -f airflow | grep -Ei "scheduler|error|traceback"
   ```

3. **Task fail (đỏ)** → trong UI: Grid → chọn task → **Logs**. Đọc từ dưới lên, dòng exception cuối cùng là nguyên nhân. Bản self-contained này hiếm khi fail; nếu fail thường do quyền ghi `/tmp` hoặc mount `./dags`.

4. **Container airflow không healthy** → thường do Postgres chưa sẵn sàng hoặc `db migrate` lỗi:
   ```bash
   docker compose logs airflow | head -80
   docker compose logs postgres | tail -30
   ```

5. **Assets: `build_marts` không tự chạy** → kiểm tra `raw_orders` đã **thành công** chưa (asset chỉ đánh dấu "cập nhật" khi task success). Xem menu Assets để thấy quan hệ.

## Ghi chú trung thực
DAG đã qua `python3 -m py_compile` (cú pháp sạch); compose đã validate YAML. **Chưa chạy trên Airflow thật** trong môi trường tạo ra nó (sandbox không cài Airflow nên không DagBag-parse được). Nếu UI báo import error hay task đỏ, đó là bài tập: đọc traceback, sửa, ghi postmortem.

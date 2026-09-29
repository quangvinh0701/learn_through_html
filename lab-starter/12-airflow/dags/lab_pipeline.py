"""Lab 12 — DAG E2E, bản SELF-CONTAINED (chạy được, không phụ thuộc ngoài).

Trích & chuyển thể từ 12-airflow-orchestration-masterclass.html
(Module 14 "Lab E2E", block dags/production_etl_pipeline.py — bản đã vá
imports/ds/success_alert).

Bản gốc gọi PostgresHook + S3 + Snowflake + Slack — KHÔNG chạy được nếu thiếu
connection/credentials. Ở đây thay bằng DỮ LIỆU GIẢ sinh tại chỗ (pure Python,
không cần pandas) để `docker compose up` là chạy xanh ngay. Giữ nguyên khung
extract -> transform -> quality_check -> success_alert và các điểm đã vá:
  - import theo Airflow 3 (airflow.sdk)
  - `ds` được Airflow inject vào tham số cùng tên
  - task `success_alert` dùng trigger_rule none_failed_min_one_success
"""
from __future__ import annotations

import csv
import os
import random
from datetime import timedelta

import pendulum
from airflow.sdk import dag, task  # Airflow 3: Task SDK

DATA_DIR = "/tmp/lab_pipeline"

default_args = {
    "owner": "data_team",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
    "retry_exponential_backoff": True,
}


@dag(
    dag_id="lab_pipeline",
    default_args=default_args,
    schedule="@daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Ho_Chi_Minh"),
    catchup=False,
    max_active_runs=1,
    tags=["lab", "etl", "self-contained"],
    doc_md=__doc__,
)
def lab_pipeline():

    # ── Step 1: Extract — sinh dữ liệu orders giả, ghi CSV ──
    @task(task_id="extract")
    def extract(ds=None) -> dict:
        # `ds` (logical date, dạng 'YYYY-MM-DD') được Airflow tự inject.
        os.makedirs(DATA_DIR, exist_ok=True)
        random.seed(ds or "seed")
        statuses = ["pending", "completed", "shipped", "cancelled"]
        rows = [
            {
                "order_id": f"ORD-{ds}-{i:04d}",
                "customer_id": f"CUST-{random.randint(1, 20):03d}",
                "amount": round(random.uniform(10_000, 2_000_000), 2),
                "status": random.choice(statuses),
                "created_at": ds,
            }
            for i in range(200)
        ]
        path = os.path.join(DATA_DIR, f"orders_{ds}.csv")
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return {"row_count": len(rows), "path": path, "ds": ds}

    # ── Step 2: Transform — gộp doanh thu theo status (thay 'dbt run') ──
    @task(task_id="transform")
    def transform(meta: dict) -> dict:
        agg: dict[str, float] = {}
        with open(meta["path"], newline="") as f:
            for r in csv.DictReader(f):
                agg[r["status"]] = agg.get(r["status"], 0.0) + float(r["amount"])
        out = os.path.join(DATA_DIR, f"revenue_{meta['ds']}.csv")
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["status", "revenue"])
            for k, v in sorted(agg.items()):
                w.writerow([k, round(v, 2)])
        return {"path": out, "groups": len(agg), "ds": meta["ds"]}

    # ── Step 3: Quality check — assert thuần Python (thay Great Expectations) ──
    @task(task_id="quality_check")
    def quality_check(meta: dict) -> dict:
        with open(meta["path"], newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) > 0, "Bảng orders rỗng"
        assert all(r["order_id"] for r in rows), "order_id có giá trị rỗng"
        assert all(float(r["amount"]) >= 0 for r in rows), "amount âm"
        valid = {"pending", "completed", "shipped", "cancelled"}
        assert {r["status"] for r in rows} <= valid, "status ngoài tập hợp lệ"
        return {"passed": True, "row_count": len(rows)}

    # ── Step 4: Alert on success — log thay cho POST Slack webhook ──
    @task(task_id="success_alert", trigger_rule="none_failed_min_one_success")
    def success_alert(ds=None) -> None:
        print(f"✅ lab_pipeline succeeded for {ds}")

    # ── Dependency graph (TaskFlow: truyền XCom qua tham số) ──
    meta = extract()
    revenue = transform(meta)
    quality = quality_check(meta)
    done = success_alert()

    [revenue, quality] >> done


lab_pipeline()

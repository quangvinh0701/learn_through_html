"""Lab 12 — Assets (data-aware scheduling) của Airflow 3.

Trích & chuyển thể từ 12-airflow-orchestration-masterclass.html
(Module 2, block "dags/assets_demo.py — Airflow 3 Assets").

Ý tưởng: DAG downstream chạy KHI DỮ LIỆU sẵn sàng (asset cập nhật), thay vì
đoán giờ bằng cron. Bản trong bài để thân hàm là `...`; ở đây điền phần thân
tối thiểu để nó chạy thật và phát tín hiệu cập nhật asset.

Ví dụ ghép với dbt (Astronomer Cosmos) nằm ở README — KHÔNG bật ở đây vì cần
cài thêm `astronomer-cosmos` + dbt, sẽ gây import error nếu để trong dags/.
"""
from __future__ import annotations

import json
import os

import pendulum
from airflow.sdk import Asset, asset, dag, task


# @asset: mỗi lần task chạy XONG THÀNH CÔNG = một lần "cập nhật asset raw_orders".
@asset(schedule="@daily")
def raw_orders():
    os.makedirs("/tmp/lab_assets", exist_ok=True)
    payload = {"rows": 123, "ts": pendulum.now().to_iso8601_string()}
    with open("/tmp/lab_assets/raw_orders.json", "w") as f:
        json.dump(payload, f)


# DAG downstream: schedule theo ASSET, không theo giờ.
# Chạy ngay khi raw_orders cập nhật (không cần ExternalTaskSensor/poll thủ công).
@dag(
    dag_id="build_marts",
    schedule=[Asset("raw_orders")],
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Ho_Chi_Minh"),
    catchup=False,
    tags=["lab", "assets"],
)
def build_marts():
    @task
    def build() -> str:
        # Dựng mart từ raw_orders (ở đây chỉ log cho gọn).
        path = "/tmp/lab_assets/raw_orders.json"
        source = json.load(open(path)) if os.path.exists(path) else {}
        print(f"Xây mart từ raw_orders: {source}")
        return "mart_built"

    build()


build_marts()

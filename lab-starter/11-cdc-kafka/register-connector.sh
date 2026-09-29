#!/usr/bin/env bash
# =============================================================
# Lab 11 CDC — register-connector.sh
# Đăng ký Debezium PostgresConnector qua REST API của Kafka Connect.
# Trích & chuyển thể từ 11-streaming-data-api-masterclass.html
#   (Module 13 Lab, block "bash — register Debezium connector").
#
# Chạy SAU khi `docker compose up -d` và kafka-connect đã healthy.
#   Trên Windows: chạy trong Git Bash / WSL, hoặc dùng lệnh curl tương đương.
# =============================================================
set -euo pipefail

CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"
CONNECTOR_NAME="lab-orders-connector"

echo ">> Đợi Kafka Connect REST API sẵn sàng tại ${CONNECT_URL} ..."
for i in $(seq 1 30); do
  if curl -sf "${CONNECT_URL}/connectors" >/dev/null 2>&1; then
    echo ">> Connect đã sẵn sàng."
    break
  fi
  echo "   ...chưa sẵn sàng (lần ${i}/30), chờ 3s"
  sleep 3
done

echo ">> Đăng ký connector '${CONNECTOR_NAME}' ..."
# bootstrap/schema-history nối tới listener NỘI BỘ kafka:29092.
# topic.prefix=cdc  ->  topic sinh ra là  cdc.public.orders / cdc.public.order_items
curl -i -X POST "${CONNECT_URL}/connectors" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "lab-orders-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "plugin.name": "pgoutput",
      "database.hostname": "postgres",
      "database.port": "5432",
      "database.user": "postgres",
      "database.password": "postgres",
      "database.dbname": "labdb",
      "table.include.list": "public.orders,public.order_items",
      "topic.prefix": "cdc",
      "snapshot.mode": "initial",
      "publication.autocreate.mode": "filtered",
      "slot.name": "debezium_slot",
      "tombstones.on.delete": "false",
      "transforms": "unwrap",
      "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
      "transforms.unwrap.delete.handling.mode": "rewrite",
      "errors.tolerance": "all",
      "errors.deadletterqueue.topic.name": "cdc.dlq",
      "errors.deadletterqueue.context.headers.enabled": true
    }
  }'

echo
echo ">> Trạng thái connector (đợi state = RUNNING):"
sleep 3
curl -s "${CONNECT_URL}/connectors/${CONNECTOR_NAME}/status" || true
echo
echo ">> Xong. Nếu state != RUNNING, xem mục 'Khi hỏng thì soi gì' trong README."

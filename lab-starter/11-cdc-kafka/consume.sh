#!/usr/bin/env bash
# =============================================================
# Lab 11 CDC — consume.sh
# Đọc topic CDC bằng kafka-console-consumer (chạy TRONG container kafka).
# Trích & chuyển thể từ 11-streaming-data-api-masterclass.html
#   (Module 13 Lab, block "bash — test với SQL" phần console-consumer).
#
# LƯU Ý QUAN TRỌNG (đã sửa so với HTML):
#   topic.prefix = "cdc" nên topic đúng là  cdc.public.orders
#   (bản HTML ghi 'cdc.dbserver.public.orders' — sai, dư 'dbserver';
#    tên đó chỉ đúng khi topic.prefix = 'dbserver').
# =============================================================
set -euo pipefail

TOPIC="${1:-cdc.public.orders}"     # truyền tham số 1 để đổi topic, vd: cdc.public.order_items
KAFKA_CONTAINER="${KAFKA_CONTAINER:-cdc-kafka}"

echo ">> Danh sách topic hiện có:"
docker exec "${KAFKA_CONTAINER}" kafka-topics --bootstrap-server localhost:9092 --list || true
echo
echo ">> Đang consume topic '${TOPIC}' từ đầu (Ctrl-C để dừng)."
echo "   Mở terminal khác chạy INSERT/UPDATE/DELETE để thấy event chảy về."
echo
docker exec -it "${KAFKA_CONTAINER}" kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic "${TOPIC}" \
  --from-beginning \
  --property print.key=true \
  --property key.separator=" | "

#!/usr/bin/env python3
"""Lab 27 — scripts/dynamodb_setup.py

Dung bang single-table `shop` tren DynamoDB Local, nap du lieu mau, roi chay
lai dung cac access pattern da liet ke o Chuong 16 de kiem chung thiet ke khoa.

    pip install boto3
    python3 dynamodb_setup.py                       # tro toi localhost:8000
    python3 dynamodb_setup.py --reset               # xoa bang roi tao lai
    python3 dynamodb_setup.py --endpoint http://dynamodb-local:8000

DynamoDB Local khong kiem tra credential, nhung boto3 VAN doi phai co.
Vi vay dat 'local'/'local' — dung nham credential that thi ban se tao bang
tren AWS va bi tinh tien.

GHI CHU TRUNG THUC: script nay da qua `py_compile` va da chay THAT mot lan
voi backend gia lap moto (xem scripts/test_logic.py). CHUA chay voi container
amazon/dynamodb-local that trong moi truong tao ra no.
"""
import argparse
import sys
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

TABLE = "shop"

ORDERS = [
    ("O-1001", "C-01", "2026-07-28T09:00:00Z", 448000, "delivered",
     [("SKU-A", 2, 199000), ("SKU-C", 1, 50000)]),
    ("O-1002", "C-01", "2026-07-29T14:20:00Z", 890000, "shipped",
     [("SKU-B", 1, 890000)]),
    ("O-1003", "C-02", "2026-07-29T15:05:00Z", 1590000, "pending",
     [("SKU-D", 1, 1590000)]),
    ("O-1004", "C-01", "2026-07-30T08:10:00Z", 275000, "pending",
     [("SKU-E", 1, 275000)]),
    ("O-1005", "C-03", "2026-07-30T08:45:00Z", 6200000, "pending",
     [("SKU-F", 1, 6200000)]),
]


def get_resource(endpoint, region):
    return boto3.resource(
        "dynamodb",
        endpoint_url=endpoint,
        region_name=region,
        aws_access_key_id="local",
        aws_secret_access_key="local",
    )


def get_client(endpoint, region):
    """Client MUC THAP rieng — KHONG dung ddb.meta.client.

    boto3.resource('dynamodb') gan them bo chuyen doi kieu (TransformationInjector)
    len chinh client cua no: no tu doi Python dict <-> AttributeValue. Neu ban goi
    transact_write_items qua resource.meta.client voi AttributeValue da viet san
    ({"S": "..."}), no se bi boc THEM mot lop nua va request thanh rac.
    Trieu chung: TransactionCanceledException voi ly do vo nghia
    ("TypeError: unhashable type: 'dict'" tren moto; ValidationException tren AWS that).
    """
    return boto3.client(
        "dynamodb",
        endpoint_url=endpoint,
        region_name=region,
        aws_access_key_id="local",
        aws_secret_access_key="local",
    )


def create_table(ddb, reset=False):
    """Mot bang, hai khoa tong quat (PK/SK), mot GSI dao nguoc theo trang thai."""
    existing = [t.name for t in ddb.tables.all()]
    if TABLE in existing:
        if not reset:
            print(f"[create] bang '{TABLE}' da ton tai — bo qua (dung --reset de tao lai)")
            return ddb.Table(TABLE)
        print(f"[create] xoa bang '{TABLE}' cu ...")
        ddb.Table(TABLE).delete()
        ddb.meta.client.get_waiter("table_not_exists").wait(TableName=TABLE)

    tbl = ddb.create_table(
        TableName=TABLE,
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        # CHI khai bao thuoc tinh nam trong khoa. Khai bao thua -> ValidationException.
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
            {"AttributeName": "GSI1PK", "AttributeType": "S"},
            {"AttributeName": "GSI1SK", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[{
            "IndexName": "GSI1",
            "KeySchema": [
                {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
            ],
            # INCLUDE thay vi ALL: GSI la mot ban sao co chi phi ghi va luu rieng.
            # Chieu cang rong, hoa don cang cao (Chuong 14, muc chi phi an).
            "Projection": {
                "ProjectionType": "INCLUDE",
                "NonKeyAttributes": ["order_id", "total", "customer_id"],
            },
        }],
        BillingMode="PAY_PER_REQUEST",
    )
    ddb.meta.client.get_waiter("table_exists").wait(TableName=TABLE)
    print(f"[create] bang '{TABLE}' -> {tbl.table_status}")
    return tbl


def seed(tbl):
    """Ba loai item song chung mot bang: Customer, Order + OrderItem, OrderRef."""
    with tbl.batch_writer() as bw:
        for cid, tier in [("C-01", "gold"), ("C-02", "std"), ("C-03", "gold")]:
            bw.put_item(Item={
                "PK": f"CUSTOMER#{cid}", "SK": "PROFILE",
                "type": "Customer", "customer_id": cid, "tier": tier,
            })
        for oid, cid, ts, total, status, items in ORDERS:
            bw.put_item(Item={
                "PK": f"ORDER#{oid}", "SK": "METADATA", "type": "Order",
                "order_id": oid, "customer_id": cid, "created_at": ts,
                "total": Decimal(total), "status": status,
                # Khoa GSI la thuoc tinh binh thuong. Item nao khong co GSI1PK
                # thi don gian KHONG xuat hien trong index (sparse index) —
                # nho do OrderItem va Customer khong lam phinh GSI1.
                "GSI1PK": f"STATUS#{status}", "GSI1SK": f"{ts}#{oid}",
            })
            for sku, qty, price in items:
                bw.put_item(Item={
                    "PK": f"ORDER#{oid}", "SK": f"ITEM#{sku}", "type": "OrderItem",
                    "order_id": oid, "sku": sku,
                    "qty": Decimal(qty), "unit_price": Decimal(price),
                })
            bw.put_item(Item={
                "PK": f"CUSTOMER#{cid}", "SK": f"ORDER#{ts}#{oid}", "type": "OrderRef",
                "order_id": oid, "total": Decimal(total), "status": status,
            })
    n = tbl.scan(Select="COUNT")["Count"]
    print(f"[seed]   tong item trong bang: {n}")


def ap5_order_detail(tbl, order_id="O-1001"):
    print(f"\n[AP-5] chi tiet don {order_id} — MOT Query, khong join")
    r = tbl.query(KeyConditionExpression=Key("PK").eq(f"ORDER#{order_id}"),
                  ReturnConsumedCapacity="TOTAL")
    for it in r["Items"]:
        print(f"   SK={it['SK']:<16} type={it['type']}")
    print(f"   Count={r['Count']}  RCU={r['ConsumedCapacity']['CapacityUnits']}")


def ap6_customer_orders(tbl, customer_id="C-01"):
    print(f"\n[AP-6] don cua {customer_id}, moi nhat truoc")
    r = tbl.query(
        KeyConditionExpression=Key("PK").eq(f"CUSTOMER#{customer_id}")
        & Key("SK").begins_with("ORDER#"),
        ScanIndexForward=False, Limit=20, ReturnConsumedCapacity="TOTAL",
    )
    for it in r["Items"]:
        print(f"   {it['SK']}  total={it['total']}  {it['status']}")
    print(f"   RCU={r['ConsumedCapacity']['CapacityUnits']}")


def ap7_orders_by_status(tbl, status="pending"):
    print(f"\n[AP-7] don dang '{status}' — Query GSI1")
    r = tbl.query(IndexName="GSI1",
                  KeyConditionExpression=Key("GSI1PK").eq(f"STATUS#{status}"),
                  ReturnConsumedCapacity="TOTAL")
    for it in r["Items"]:
        print(f"   {it['GSI1SK']}  {it['order_id']}  total={it['total']}")
    print(f"   Count={r['Count']}  RCU={r['ConsumedCapacity']['CapacityUnits']}")
    return r["Count"]


def scan_the_wrong_way(tbl, status="pending"):
    """Cung cau hoi, lam bang Scan — de do ScannedCount va thay cai gia."""
    print(f"\n[SAI]  Scan + FilterExpression cho cung cau hoi")
    r = tbl.scan(FilterExpression=Attr("status").eq(status) & Attr("type").eq("Order"),
                 ReturnConsumedCapacity="TOTAL")
    print(f"   tra ve {r['Count']} item nhung DOC {r['ScannedCount']} item "
          f"({r['ScannedCount'] / max(r['Count'], 1):.1f} lan)")
    print("   DynamoDB tinh tien theo BYTE DA QUET, khong theo so item tra ve.")


def transact_ship(client, order_id="O-1003"):
    """Doi trang thai + ghi audit trong mot giao dich. Chay lai se bi tu choi."""
    print(f"\n[TX]   doi {order_id} pending -> shipped kem ban ghi audit")
    try:
        client.transact_write_items(TransactItems=[
            {"Update": {
                "TableName": TABLE,
                "Key": {"PK": {"S": f"ORDER#{order_id}"}, "SK": {"S": "METADATA"}},
                "UpdateExpression": "SET #s = :new, GSI1PK = :gpk",
                "ConditionExpression": "#s = :old",
                "ExpressionAttributeNames": {"#s": "status"},
                "ExpressionAttributeValues": {
                    ":new": {"S": "shipped"}, ":old": {"S": "pending"},
                    ":gpk": {"S": "STATUS#shipped"},
                },
            }},
            {"Put": {
                "TableName": TABLE,
                "Item": {
                    "PK": {"S": f"ORDER#{order_id}"},
                    "SK": {"S": "AUDIT#2026-07-30T09:00:00Z"},
                    "type": {"S": "Audit"}, "from": {"S": "pending"},
                    "to": {"S": "shipped"}, "actor": {"S": "ops@shop"},
                },
            }},
        ])
        print("   OK — ca hai thao tac cung commit")
    except ClientError as e:
        print(f"   {e.response['Error']['Code']}: dieu kien khong con dung "
              f"(chay lan hai la dung nhu vay)")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Dung single-table 'shop' tren DynamoDB Local")
    ap.add_argument("--endpoint", default="http://localhost:8000")
    ap.add_argument("--region", default="ap-southeast-1")
    ap.add_argument("--reset", action="store_true", help="xoa bang cu roi tao lai")
    args = ap.parse_args(argv)

    print(f"endpoint = {args.endpoint}  region = {args.region}")
    ddb = get_resource(args.endpoint, args.region)
    try:
        tbl = create_table(ddb, reset=args.reset)
    except Exception as e:
        print(f"KHONG NOI DUOC toi {args.endpoint}: {type(e).__name__}: {e}")
        print("Kiem tra: docker compose ps | grep dynamodb  va  curl http://localhost:8000")
        return 1

    cli = get_client(args.endpoint, args.region)
    seed(tbl)
    ap5_order_detail(tbl)
    ap6_customer_orders(tbl)
    ap7_orders_by_status(tbl)
    scan_the_wrong_way(tbl)
    transact_ship(cli)
    transact_ship(cli)                  # lan hai phai bi tu choi
    ap7_orders_by_status(tbl)           # con 2 don pending
    print("\nXong. Bai tap tiep theo o README, muc 'Bai tap'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

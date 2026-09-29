#!/usr/bin/env python3
"""Chay toan bo logic cua dynamodb_setup.py tren backend gia lap moto.

Muc dich: chung minh phan THIET KE KHOA va cac cau Query la dung, ma khong
can Docker. Khong thay the duoc viec chay that — moto khong mo phong trung
thuc ConsumedCapacity, gioi han 400 KB moi item, hay throttling.

    pip install "moto[dynamodb]" boto3
    python3 test_logic.py
"""
import sys

import boto3
from moto import mock_aws

import dynamodb_setup as S


@mock_aws
def run():
    ddb = boto3.resource("dynamodb", region_name="ap-southeast-1")
    tbl = S.create_table(ddb, reset=False)
    S.seed(tbl)
    S.ap5_order_detail(tbl)
    S.ap6_customer_orders(tbl)
    n = S.ap7_orders_by_status(tbl)
    S.scan_the_wrong_way(tbl)
    cli = boto3.client("dynamodb", region_name="ap-southeast-1")
    S.transact_ship(cli)
    S.transact_ship(cli)
    n_after = S.ap7_orders_by_status(tbl)
    assert n == 3, f"ky vong 3 don pending, nhan {n}"
    assert n_after == 2, f"sau khi ship 1 don phai con 2 pending, nhan {n_after}"
    print("\nTAT CA KIEM TRA DAT.")


if __name__ == "__main__":
    run()
    sys.exit(0)

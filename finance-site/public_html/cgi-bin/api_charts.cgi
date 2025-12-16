#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import pymysql
from http import cookies

print("Content-Type: application/json\n")

DB_HOST = "localhost"
DB_USER = "user"
DB_PASS = "1111"
DB_NAME = "finance"

def get_conn():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

try:
    c = cookies.SimpleCookie(os.environ.get("HTTP_COOKIE", ""))
    if "user_id" not in c:
        print(json.dumps({"error": "auth"}))
        sys.exit()

    user_id = int(c["user_id"].value)

    params = os.environ.get("QUERY_STRING", "")
    where_date = ""

    if "month=" in params:
        month = params.split("month=")[1][:7]  # YYYY-MM
        where_date = "AND DATE_FORMAT(created_at, '%Y-%m') = %s"

    conn = get_conn()
    cur = conn.cursor()

    sql = f"""
        SELECT category, type, SUM(amount) as total
        FROM transactions
        WHERE user_id = %s {where_date}
        GROUP BY category, type
    """

    if where_date:
        cur.execute(sql, (user_id, month))
    else:
        cur.execute(sql, (user_id,))

    rows = cur.fetchall()
    print(json.dumps(rows, default=str))

except Exception as e:
    print(json.dumps({
        "error": "server error",
        "details": str(e)
    }))

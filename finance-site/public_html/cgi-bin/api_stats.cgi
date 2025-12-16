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

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS income,
            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS expense
        FROM transactions
        WHERE user_id = %s
    """, (user_id,))

    row = cur.fetchone()

    income = float(row["income"] or 0)
    expense = float(row["expense"] or 0)

    print(json.dumps({
        "income": income,
        "expense": expense,
        "balance": income - expense
    }))

except Exception as e:
    print(json.dumps({
        "error": "server error",
        "details": str(e)
    }))

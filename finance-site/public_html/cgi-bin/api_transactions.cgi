#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
import pymysql
from http import cookies
from datetime import datetime


DB_HOST = "localhost"
DB_USER = "user"
DB_PASS = "1111"
DB_NAME = "finance"

print("Content-Type: application/json\n")

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

    if os.environ.get("REQUEST_METHOD") == "POST":
        raw = sys.stdin.read()
        if not raw:
            print(json.dumps({"error": "empty request"}))
            sys.exit()

        data = json.loads(raw)

        amount = float(data["amount"])
        category = data["category"]
        description = data.get("description", "")
        type_ = data.get("type", "expense")

        cur.execute(
            """
            INSERT INTO transactions
            (user_id, amount, category, description, type, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, amount, category, description, type_, datetime.now())
        )
        conn.commit()

        print(json.dumps({"ok": True}))
        sys.exit()

    cur.execute(
        """
        SELECT amount, category, description, type, created_at
        FROM transactions
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    rows = cur.fetchall()
    print(json.dumps(rows, default=str))

except Exception as e:
    print(json.dumps({
        "error": "server error",
        "details": str(e)
    }))

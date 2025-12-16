#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pymysql
from http.cookies import SimpleCookie
import os, sys

print("Content-Type: application/json\n")

def get_conn():
    return pymysql.connect(
        host="localhost",
        user="user",
        password="1111",
        database="finance",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

try:
    cookie = SimpleCookie(os.environ.get("HTTP_COOKIE", ""))
    if "user_id" not in cookie:
        print(json.dumps({"error": "auth"}))
        sys.exit()

    user_id = cookie["user_id"].value

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT email, full_name FROM users WHERE id=%s",
        (user_id,)
    )

    user = cur.fetchone()
    if not user:
        print(json.dumps({"error": "not found"}))
        sys.exit()

    print(json.dumps({
        "ok": True,
        "email": user["email"],
        "full_name": user["full_name"]
    }))

except Exception as e:
    print(json.dumps({
        "error": "server error",
        "details": str(e)
    }))

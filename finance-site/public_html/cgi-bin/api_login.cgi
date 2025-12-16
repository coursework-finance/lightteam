#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import traceback
import hashlib
import pymysql
from http.cookies import SimpleCookie

def respond(data, cookie=None):
    print("Content-Type: application/json")
    if cookie:
        print(cookie.output())
    print()
    print(json.dumps(data))
    sys.exit()

try:
    raw = sys.stdin.read().strip()
    if not raw:
        respond({"error": "empty request"})

    data = json.loads(raw)
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        respond({"error": "email and password required"})

    pwd_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = pymysql.connect(
        host="localhost",
        user="user",
        password="1111",
        database="finance",
        charset="utf8mb4"
    )

    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM users WHERE email=%s AND password_hash=%s",
        (email, pwd_hash)
    )

    row = cur.fetchone()
    if not row:
        respond({"error": "invalid login or password"})

    cookie = SimpleCookie()
    cookie["user_id"] = str(row[0])
    cookie["user_id"]["path"] = "/"

    respond({"ok": True}, cookie)

except Exception:
    respond({
        "error": "server error",
        "trace": traceback.format_exc()
    })

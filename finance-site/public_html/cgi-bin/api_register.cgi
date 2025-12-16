#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import hashlib
import traceback
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
    full_name = data.get("full_name", "")

    if not email or not password:
        respond({"error": "email and password required"})


    conn = pymysql.connect(
        host="localhost",
        user="user",
        password="1111",
        db="finance",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        respond({"error": "email exists"})

    pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    cur.execute(
        "INSERT INTO users (email, password_hash, full_name) VALUES (%s,%s,%s)",
        (email, pwd_hash, full_name)
    )
    conn.commit()

    uid = cur.lastrowid

    cookie = SimpleCookie()
    cookie["user_id"] = str(uid)
    cookie["user_id"]["path"] = "/"

    respond({"ok": True}, cookie)

except Exception:
    respond({
        "error": "server error",
        "trace": traceback.format_exc()
    })
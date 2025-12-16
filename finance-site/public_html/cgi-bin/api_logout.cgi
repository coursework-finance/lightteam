#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from http.cookies import SimpleCookie

print("Content-Type: application/json")

cookie = SimpleCookie()
cookie["user_id"] = ""
cookie["user_id"]["path"] = "/"
cookie["user_id"]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"

print(cookie.output())
print()
print(json.dumps({"ok": True}))

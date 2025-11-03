"""Small helper to POST a test Telegram-like update to a webhook endpoint.

Usage:
  python test_send_update.py --url http://localhost:8080/ --secret <secret> --text "hello"

This uses only the standard library so no extra dependencies are required.
"""
from __future__ import annotations

import argparse
import json
import time
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError


def build_update(text: str, user_id: int = 111111, username: str = "tester") -> dict:
    now = int(time.time())
    return {
        "update_id": now,
        "message": {
            "message_id": 1,
            "from": {"id": user_id, "is_bot": False, "first_name": username, "username": username},
            "chat": {"id": user_id, "type": "private"},
            "date": now,
            "text": text,
        },
    }


def send_update(url: str, secret: str, update: dict) -> None:
    data = json.dumps(update).encode("utf-8")
    req = urlrequest.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if secret:
        req.add_header("X-Telegram-Bot-Api-Secret-Token", secret)

    try:
        with urlrequest.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            print("Response:", resp.status, resp.reason)
            if body:
                print(body)
    except HTTPError as e:
        print("HTTP error:", e.code, e.reason)
        try:
            print(e.read().decode("utf-8"))
        except Exception:
            pass
    except URLError as e:
        print("Failed to reach server:", e)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="Webhook URL (e.g. http://localhost:8080/)")
    p.add_argument("--secret", default="", help="Webhook secret token to include in header")
    p.add_argument("--text", default="hello", help="Message text to send")
    args = p.parse_args()

    update = build_update(args.text)
    print("Sending update to", args.url)
    send_update(args.url, args.secret, update)


if __name__ == "__main__":
    main()

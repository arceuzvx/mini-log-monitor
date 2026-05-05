import time
import re
import os
import requests
import hashlib

LOG_FILE = os.getenv("LOG_FILE", "/logs/app.log")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")

PATTERNS = [r"Failed login", r"ERROR", r"CRITICAL", r"unauthorized"]
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PATTERNS]

COOLDOWN = int(os.getenv("COOLDOWN_SECONDS", 30))

last_position = 0
last_alert_time = 0
last_alert_hash = None


def read_new_lines():
    global last_position

    try:
        current_size = os.path.getsize(LOG_FILE)

        # Handle log rotation / truncation
        if current_size < last_position:
            last_position = 0

        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(last_position)
            new_lines = f.readlines()
            last_position = f.tell()

        return new_lines

    except FileNotFoundError:
        return []


def generate_hash(matches):
    return hashlib.md5("".join(matches).encode()).hexdigest()


def check_new_lines():
    global last_alert_time, last_alert_hash

    new_lines = read_new_lines()
    if not new_lines:
        return

    matches = [
        line for line in new_lines
        if any(p.search(line) for p in COMPILED_PATTERNS)
    ]

    if not matches:
        return

    # Deduplication via hash
    current_hash = generate_hash(matches)
    if current_hash == last_alert_hash:
        return

    now = time.time()

    # Cooldown control
    if now - last_alert_time < COOLDOWN:
        print("Cooldown active, skipping alert")
        return

    last_alert_time = now
    last_alert_hash = current_hash

    send_slack_alert(matches)


def send_slack_alert(matches):
    preview = matches[:10]

    payload = {
        "text": "Suspicious activity detected",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*mini-log-monitor alert*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(f"- {m.strip()}" for m in preview)
                }
            }
        ]
    }

    if SLACK_WEBHOOK:
        try:
            requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
            print(f"Alert sent ({len(matches)} matches)")
        except Exception as e:
            print(f"Slack send failed: {e}")
    else:
        print("No webhook set. Alert:\n", payload)


if __name__ == "__main__":
    # Initialize position to end of file
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, 2)
            last_position = f.tell()
    else:
        print(f"Waiting for log file: {LOG_FILE}")

    print(f"Monitoring {LOG_FILE}...")

    # Polling loop (more reliable than watchdog in Docker)
    while True:
        check_new_lines()
        time.sleep(1)
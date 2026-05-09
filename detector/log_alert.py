import time
import re
import os
import requests
import hashlib
from collections import defaultdict, deque

LOG_FILE = os.getenv("LOG_FILE", "/logs/app.log")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")

COOLDOWN = int(os.getenv("COOLDOWN_SECONDS", 30))

# Detection tuning
BRUTE_FORCE_THRESHOLD = int(os.getenv("BF_THRESHOLD", 5))   # attempts
BF_WINDOW = int(os.getenv("BF_WINDOW", 60))                 # seconds

PATTERNS = [r"Failed login", r"ERROR", r"CRITICAL", r"unauthorized"]
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PATTERNS]

IP_REGEX = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")

last_position = 0
last_alert_time = 0
last_alert_hash = None

# Track attempts per IP within time window
ip_attempts = defaultdict(lambda: deque())


def read_new_lines():
    global last_position

    try:
        current_size = os.path.getsize(LOG_FILE)

        # Handle log rotation
        if current_size < last_position:
            last_position = 0

        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(last_position)
            lines = f.readlines()
            last_position = f.tell()

        return lines

    except FileNotFoundError:
        return []


def extract_ips(line):
    match = IP_REGEX.search(line)
    return match.group() if match else None


def update_ip_tracking(ip):
    now = time.time()
    dq = ip_attempts[ip]
    dq.append(now)

    # Remove old timestamps outside window
    while dq and now - dq[0] > BF_WINDOW:
        dq.popleft()

    return len(dq)


def generate_hash(data):
    return hashlib.md5(str(data).encode()).hexdigest()


def send_slack_alert(message_lines):
    payload = {
        "text": "Security Alert",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*🚨 Security Alert*"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "\n".join(message_lines)}
            }
        ]
    }

    if SLACK_WEBHOOK:
        try:
            requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
            print("Alert sent")
        except Exception as e:
            print(f"Slack error: {e}")
    else:
        print("No webhook set:", payload)


def process_lines(lines):
    global last_alert_time, last_alert_hash

    alerts = []

    for line in lines:
        if not any(p.search(line) for p in COMPILED_PATTERNS):
            continue

        ip = extract_ips(line)
        if not ip:
            continue

        count = update_ip_tracking(ip)

        if count >= BRUTE_FORCE_THRESHOLD:
            alerts.append(f"Brute force detected from {ip} ({count} attempts)")

    if not alerts:
        return

    # Dedup
    current_hash = generate_hash(alerts)
    if current_hash == last_alert_hash:
        return

    # Cooldown
    now = time.time()
    if now - last_alert_time < COOLDOWN:
        print("Cooldown active")
        return

    last_alert_time = now
    last_alert_hash = current_hash

    send_slack_alert(alerts)


if __name__ == "__main__":
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, 2)
            last_position = f.tell()

    print(f"Monitoring {LOG_FILE}")

    while True:
        new_lines = read_new_lines()
        if new_lines:
            process_lines(new_lines)
        time.sleep(1)
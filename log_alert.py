#!/usr/bin/env python3
import re, os
import requests

# ---------------- CONFIG ----------------
LOG_FILE = r"sample.log"  # path to your Windows log or test log
ALERT_THRESHOLD = 3              # number of failed events to trigger alert
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")  # set in env

# Keywords to watch
PATTERNS = [r"Failed login attempt"]

# ---------------- FUNCTIONS ----------------
def read_logs(log_file):
    """Read all lines from the log file."""
    with open(log_file, "r") as f:
        return [line.strip() for line in f]

def match_patterns(events, patterns):
    """Return lines that match any of the patterns."""
    matches = []
    for line in events:
        for pat in patterns:
            if re.search(pat, line, re.IGNORECASE):
                matches.append(line)
    return matches

def send_slack_alert(matches):
    if not matches:
        return
    text = "*Mini Log Alert Bot* — Suspicious events detected:\n"
    text += "\n".join(f"- {m}" for m in matches[:20])
    payload = {"text": text}
    if not SLACK_WEBHOOK:
        print("SLACK_WEBHOOK not set, printing alert instead:\n", text)
        return
    try:
        requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
        print("Alert sent to Slack.")
    except Exception as e:
        print(f"Failed to send alert: {e}")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    events = read_logs(LOG_FILE)
    matches = match_patterns(events, PATTERNS)
    if len(matches) >= ALERT_THRESHOLD:
        send_slack_alert(matches)
    else:
        print(f"No alerts. Found {len(matches)} suspicious events in the log.")

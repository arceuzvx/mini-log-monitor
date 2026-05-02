import time, re, os
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_FILE = os.getenv("LOG_FILE", "/logs/app.log")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
PATTERNS = [r"Failed login", r"ERROR", r"CRITICAL", r"unauthorized"]
COOLDOWN = int(os.getenv("COOLDOWN_SECONDS", 30))  # don't re-alert within 30s

last_position = 0        # track where we last read up to
last_alert_time = 0      # cooldown tracker

def read_new_lines():
    """Only read lines added since last check."""
    global last_position
    with open(LOG_FILE, "r") as f:
        f.seek(last_position)        # jump to where we left off
        new_lines = f.readlines()
        last_position = f.tell()     # save new position
    return new_lines

def check_new_lines():
    global last_alert_time
    new_lines = read_new_lines()
    if not new_lines:
        return
    matches = [l for l in new_lines for p in PATTERNS if re.search(p, l, re.IGNORECASE)]
    if not matches:
        return
    now = time.time()
    if now - last_alert_time < COOLDOWN:
        print(f"Cooldown active, skipping alert for: {matches}")
        return
    last_alert_time = now
    send_slack_alert(matches)

def send_slack_alert(matches):
    text = "*[mini-log-monitor]* Suspicious events:\n" + "\n".join(f"- {m.strip()}" for m in matches[:20])
    if SLACK_WEBHOOK:
        try:
            requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=5)
            print(f"Alert sent: {len(matches)} matches")
        except Exception as e:
            print(f"Slack send failed: {e}")
    else:
        print("No webhook set. Alert:\n", text)

class LogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.basename(event.src_path) == os.path.basename(LOG_FILE):
            check_new_lines()

if __name__ == "__main__":
    # initialise position to end of file so we only catch NEW events
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            f.seek(0, 2)             # seek to end
            globals()["last_position"] = f.tell()
    else:
        print(f"Warning: {LOG_FILE} doesn't exist yet, will watch for creation")

    observer = Observer()
    observer.schedule(LogHandler(), path=os.path.dirname(LOG_FILE) or ".", recursive=False)
    observer.start()
    print(f"Watching {LOG_FILE} for new events...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
from flask import Flask, render_template, redirect
import logging
import json
import os
from datetime import datetime

app = Flask(__name__)

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "auth.log")

os.makedirs(LOG_DIR, exist_ok=True)

# Fake creds
VALID_USERS = {
    "admin": "password123",
    "alice": "alice123",
    "bob": "bob123"
}

#logging setup

logger = logging.getLogger("auth_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
logger.addHandler(file_handler)

def log_event(event_type, username, ip, status):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "username": username,
        "ip": ip,
        "status": status,
        "endpoint": "/login"
    }
    logger.info(json.dumps(log_entry))

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        if username in VALID_USERS and VALID_USERS[username] == password:
            log_event(
                event_type="login_attempt",
                username=username,
                ip=ip,
                status="success"
            )

            return f"Welcome, {username}!"
        
        else:
            log_event(
                event_type="login_attempt",
                username=username,
                ip=ip,
                status="failed"
            )
            
            return "Invalid credentials", 401
        
        return render_template("login.html")

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
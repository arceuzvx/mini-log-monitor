# 🦉 Mini Log Monitor (Slack Alerts)

A lightweight starter project to monitor logs and send suspicious events to Slack.  
Currently works with **sample logs**, and will be extended to support **Windows Event Logs** and **Linux syslog**.

## 🛠️ Features
- Parse log files for suspicious events (e.g., failed logins).
- Send alerts to a Slack channel using a webhook (or print to console if not set).
- Simple config inside the script.
--- 

## ⚡ Quickstart

1. Clone this repo:
```bash
   git clone https://github.com/yourusername/mini-log-monitor.git
   cd mini-log-monitor
```

2. Install dependencies in venv:
```bash
python -m venv venv
venv\Scripts\activate #windows
pip install -r requirements.txt
```

3. Add your Slack webhook:
On Windows, open your terminal:
```powershell
$env:SLACK_WEBHOOK="https://hooks.slack.com/services/XXX/YYY/ZZZ"
```
4. Run the script:
```powershell
python log_alert.py
```
🚨 Alerts will be sent to your slack channel if any suspicious activity is detected.
---

Look at [SETUP.md](SETUP.md) to understand how to create your Slack webhook.
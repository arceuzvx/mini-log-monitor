# Mini Log Monitor

A containerized, rule-based log monitoring and alerting system designed for real-time detection of suspicious activity, with extensibility for DevSecOps and security operations workflows.

---

## Overview

Mini Log Monitor continuously monitors application logs, detects suspicious patterns (e.g., brute-force login attempts), and sends structured alerts to Slack via webhook.

Key design principles:
- Deterministic rule-based detection
- Low resource usage
- Container-first deployment
- Extensible for advanced security features

---

## Architecture
Log Source → File System (mounted volume)
↓
Log Monitor (Python service)
↓
Detection Engine (rules + thresholds)
↓
Slack Alerts


### Optional Extended Pipeline
Logs → Fluent Bit → Elasticsearch → Kibana
↓
Log Monitor
↓
Slack


---

## Features

### Detection
- Regex-based pattern matching
- Brute-force detection:
  - Per-IP tracking
  - Sliding time window
  - Configurable thresholds
- Rate-aware severity classification

### Reliability
- Handles log rotation
- UTF-8 tolerant (`errors="ignore"`)
- Stateful file offset tracking
- Deduplication using hashing

### Alerting
- Structured Slack alerts
- Cooldown to prevent spam
- Per-IP suppression support

### Performance
- Lightweight polling loop
- Low CPU usage (~0.1–0.3%)
- Precompiled regex patterns

---

## Project Structure
```bash
mini-log-monitor/
│
├── logs/
│ ├── app.log
│ └── .gitkeep
│
├── logalert.py
├── analyze.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── .gitignore
└── setup.md
```
---

## Configuration

Environment variables:
```
SLACK_WEBHOOK=https://hooks.slack.com/services/XXX/YYY/ZZZ

LOG_FILE=/logs/app.log
COOLDOWN_SECONDS=30
BF_THRESHOLD=5
BF_WINDOW=60
```

---

## Docker Usage

### Build and Run
docker compose up --build
## Detection Logic

### Brute Force Detection

Triggered when:


N failed attempts from same IP within time window


Where:
- N = BF_THRESHOLD
- Window = BF_WINDOW seconds

---

### Example Test


for i in {1..6}; do
echo "Failed login from 192.168.1.10" >> logs/app.log
done


---

## Alert Output

Example Slack alert:


Brute Force Detected

IP: 192.168.1.10
Attempts: 6
Window: 60s
Severity: MEDIUM


---

## Testing

### Single trigger


echo "ERROR test trigger" >> logs/app.log


### Continuous simulation


while true; do
echo "Failed login from 192.168.1.$((RANDOM%255))" >> logs/app.log
sleep 1
done


---

## Troubleshooting

### No alerts
- Verify SLACK_WEBHOOK is set
- Check inside container:

docker exec -it <container> env | grep SLACK_WEBHOOK


### No logs detected
- Check volume mapping:

./logs:/logs

- Ensure file path:

/logs/app.log


### Encoding issues
- Uses UTF-8 with fallback:

encoding="utf-8", errors="ignore"


---

## Limitations

- Rule-based detection only
- Single log source
- No persistence layer
- No built-in SIEM integration

---

## Roadmap

### Detection
- IP reputation lookup (AbuseIPDB)
- GeoIP enrichment
- Multi-pattern correlation

### DevOps
- Fluent Bit integration
- Elasticsearch + Kibana dashboards
- CI/CD improvements via GitHub Actions

### Observability
- Prometheus metrics
- Health endpoints
- Structured JSON logging

### Advanced
- Slack bot for on-demand analysis
- AI-assisted summarization (optional)
- Multi-container attack simulation

---

## Security Considerations

- Do not commit `.env`
- Treat Slack webhook as a secret
- Validate external API integrations
- Avoid log injection risks

---

## Tech Stack

- Python 3.11
- Docker / Docker Compose
- Slack Webhooks
- Regex-based detection engine

---

## Summary

Mini Log Monitor is a lightweight, extensible log monitoring system demonstrating:

- Detection engineering
- DevOps container workflows
- Alerting pipeline design
- SOC-style analysis fundamentals

It is designed to be simple, explainable, and incrementally extensible.

Look at [SETUP.md](SETUP.md) to understand how to create your Slack webhook.
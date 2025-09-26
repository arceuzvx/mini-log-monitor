# 🔧 Setup Guide — Slack App & Webhook

This project uses a Slack **Incoming Webhook** to send alerts from log files to a Slack channel.  
Follow these steps to create your own Slack app and get a webhook URL.

---

## 1. Create a Slack App
1. Go to the [Slack API Dashboard](https://api.slack.com/apps).
2. Click **Create New App** → **From scratch**.
3. Give your app a name (e.g., `MiniLogMonitorBot`) and select your workspace.

---

## 2. Add Incoming Webhooks
1. In the left sidebar, go to **Incoming Webhooks**.
2. Toggle **Activate Incoming Webhooks** → ON.
3. Click **Add New Webhook to Workspace**.
4. Choose the channel where alerts should be posted.
5. Copy the **Webhook URL** (looks like `https://hooks.slack.com/services/T000.../B000.../XXXX`).

---

## 3. Update the Project
- Open `log_alert.py`.
- Find the config section at the top:
  ```python
  SLACK_WEBHOOK = "https://hooks.slack.com/services/XXXX/XXXX/XXXX"

## 4. Test It
Run the script with the sample logs:
```powershell
python log_alert.py
```
If everything is correct, you’ll see a Slack message like:
```lua
Date: 09/27/2025 08:15:32 AM - Event: Failed login attempt - User: Bob
- Date: 09/27/2025 08:16:45 AM - Event: Failed login attempt - User: Carol
...
```
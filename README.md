# deploy-notify

> Webhook bridge that sends structured deployment summaries to Slack or Discord.

---

## Installation

```bash
pip install deploy-notify
```

Or install from source:

```bash
git clone https://github.com/yourname/deploy-notify.git && cd deploy-notify && pip install .
```

---

## Usage

Set your webhook URL as an environment variable, then call the CLI or use the Python API.

**CLI:**

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

deploy-notify send \
  --platform slack \
  --service "api-server" \
  --version "v2.4.1" \
  --status success \
  --author "jane"
```

**Python API:**

```python
from deploy_notify import Notifier

notifier = Notifier(platform="discord", webhook_url="https://discord.com/api/webhooks/...")

notifier.send(
    service="api-server",
    version="v2.4.1",
    status="success",
    author="jane"
)
```

Both Slack and Discord are supported. The `status` field accepts `success`, `failure`, or `in-progress`.

---

## Configuration

| Environment Variable    | Description                        |
|-------------------------|------------------------------------|
| `SLACK_WEBHOOK_URL`     | Incoming webhook URL for Slack     |
| `DISCORD_WEBHOOK_URL`   | Incoming webhook URL for Discord   |

---

## License

MIT © 2024 yourname
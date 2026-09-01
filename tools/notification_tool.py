"""
Tool 5/5: notification_tool

Stubbed dispatch of the final report to Slack/email. Swap `_send_slack` /
`_send_email` for real integrations (Slack Incoming Webhook, SES/SendGrid).
This tool is only ever called *after* the human approval gate in
workflows/orchestrator.py, never autonomously.
"""
from agents import function_tool
import config


def _send_slack(message: str) -> bool:
    if config.SLACK_WEBHOOK_URL:
        # import requests
        # requests.post(config.SLACK_WEBHOOK_URL, json={"text": message})
        pass
    return True


def _send_email(to: str, subject: str, body: str) -> bool:
    # Real integration point: SES / SendGrid / SMTP.
    return True


def send_notification(channel: str, message: str) -> dict:
    """Plain (non-agent-callable) function the orchestrator uses directly,
    after human approval, so dispatch never happens as a side effect of an
    LLM tool call."""
    if channel == "slack":
        ok = _send_slack(message)
    elif channel == "email":
        ok = _send_email(config.NOTIFICATION_EMAIL, "Executive Report Ready", message)
    else:
        return {"sent": False, "error": f"unknown channel '{channel}'"}

    return {"sent": ok, "channel": channel}


@function_tool
def notification_tool(channel: str, message: str) -> dict:
    """Send the approved executive report/notification to a channel.

    Args:
        channel: 'slack' or 'email'.
        message: The message body to send.
    """
    return send_notification(channel, message)

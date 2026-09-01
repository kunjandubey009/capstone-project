"""Global configuration for the AI Autonomous Business Operations Platform."""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "ops-team@example.com")

# Model used by every agent. Override per-agent if you want a cheaper/faster
# model for simple steps (e.g. Research) and a stronger one for reasoning
# steps (e.g. Domain Expert, Reviewer).
DEFAULT_MODEL = os.getenv("AGENTS_MODEL", "gpt-4.1")

# Retry policy when the Reviewer Agent rejects a stage.
MAX_REVIEW_RETRIES = 2

# Where generated executive reports are written.
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

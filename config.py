import os
from dotenv import load_dotenv

load_dotenv()

def require_env(key: str) -> str:
    val = os.getenv(key, "").strip()
    if not val:
        raise EnvironmentError(f"Missing required env variable: {key}")
    return val

def optional_int(key: str, default: int) -> int:
    raw = os.getenv(key, "").strip()
    return int(raw) if raw.isdigit() else default

def optional_role(key: str) -> int | None:
    raw = os.getenv(key, "").strip()
    return int(raw) if raw.isdigit() else None

DISCORD_TOKEN = require_env("DISCORD_TOKEN")
NOTIFICATION_CHANNEL_ID = int(require_env("NOTIFICATION_CHANNEL_ID"))

NOTIFY_BEFORE_MINUTES = optional_int("NOTIFY_BEFORE_MINUTES", 60)
POLL_INTERVAL_MINUTES = optional_int("POLL_INTERVAL_MINUTES", 10)

DIVISION_ROLES = {
    "Div. 1":       optional_role("ROLE_DIV1"),
    "Div. 2":       optional_role("ROLE_DIV2"),
    "Div. 3":       optional_role("ROLE_DIV3"),
    "Div. 4":       optional_role("ROLE_DIV4"),
    "Educational":  optional_role("ROLE_EDUCATIONAL"),
    "Global Round": optional_role("ROLE_GLOBAL"),
    "Other":        optional_role("ROLE_OTHER"),
}

"""Run from the repository root: python scripts/exasol_admin.py init|health|retry."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_environment():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env.local", override=False)


def main():
    load_environment()
    from backend.app.db import exasol_client, analytics_outbox
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "health", "retry"])
    action = parser.parse_args().action
    try:
        if action == "init":
            exasol_client.initialize_schema()
            print("Exasol schema initialized.")
        elif action == "health":
            print(exasol_client.health())
        else:
            analytics_outbox.initialize_outbox()
            print(analytics_outbox.flush())
    except exasol_client.AnalyticsUnavailable as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

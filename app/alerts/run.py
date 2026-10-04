"""CLI entrypoint for running the daily deadline scanner and alert dispatcher."""
import argparse
from datetime import date
from app.alerts.store import ensure_alert_tables
from app.alerts.dispatcher import dispatch_alerts


def main():
    parser = argparse.ArgumentParser(description="Run daily compliance deadline alerts.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without sending or writing logs.")
    parser.add_argument("--today", type=str, help="Override today's date (YYYY-MM-DD) for testing.")
    args = parser.parse_args()

    ensure_alert_tables()
    scan_date = date.fromisoformat(args.today) if args.today else date.today()

    print(f"--- Running Deadline Alerts Scanner [Date: {scan_date}] ---")
    results = dispatch_alerts(today=scan_date, dry_run=args.dry_run)
    print(f"Results: {results}")
    print("--- Done ---")


if __name__ == "__main__":
    main()
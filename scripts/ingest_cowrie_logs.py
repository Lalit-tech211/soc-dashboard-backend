import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, init_db
from app.models import Event

LOG_FILE = os.path.join(os.path.dirname(__file__), "cowrie_raw_backup.json")

def parse_timestamp(ts_str):
    # Cowrie timestamps look like "2026-08-11T00:01:47.617843Z"
    return datetime.strptime(ts_str.split(".")[0], "%Y-%m-%dT%H:%M:%S")

def main():
    init_db()
    db = SessionLocal()

    inserted = 0
    skipped = 0

    with open(LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue

            event_id = data.get("eventid", "")

            # Only ingest events that are meaningful for the dashboard
            relevant_events = [
                "cowrie.session.connect",
                "cowrie.login.success",
                "cowrie.login.failed",
                "cowrie.command.input",
            ]
            if event_id not in relevant_events:
                continue

            event = Event(
                event_id=event_id,
                session_id=data.get("session"),
                src_ip=data.get("src_ip"),
                username=data.get("username"),
                password=data.get("password"),
                timestamp=parse_timestamp(data["timestamp"]),
            )
            db.add(event)
            inserted += 1

    db.commit()
    db.close()
    print(f"Inserted {inserted} events. Skipped {skipped} malformed lines.")

if __name__ == "__main__":
    main()
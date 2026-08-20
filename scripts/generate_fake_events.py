import random
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, init_db
from app.models import Event

# A pool of realistic fake IPs, usernames, passwords
FAKE_IPS = [
    "185.220.101.45", "45.155.205.233", "103.145.13.201",
    "194.180.48.100", "89.248.165.74", "62.171.146.196",
    "185.156.73.54", "5.188.206.194", "80.94.95.116",
    "192.241.220.19",
]

USERNAMES = ["root", "admin", "pi", "ubuntu", "test", "oracle", "guest", "user"]
PASSWORDS = ["123456", "admin", "root", "toor", "raspberry", "password", "12345678", "qwerty"]

EVENT_TYPES = ["cowrie.login.failed", "cowrie.login.success", "cowrie.session.connect"]

def generate_event(base_time):
    ip = random.choice(FAKE_IPS)
    event_type = random.choices(EVENT_TYPES, weights=[70, 10, 20])[0]
    offset_minutes = random.randint(0, 60 * 24 * 5)  # spread across 5 days
    timestamp = base_time - timedelta(minutes=offset_minutes)

    return Event(
        event_id=event_type,
        session_id=f"session_{random.randint(1000,9999)}",
        src_ip=ip,
        username=random.choice(USERNAMES) if "login" in event_type else None,
        password=random.choice(PASSWORDS) if "login" in event_type else None,
        timestamp=timestamp,
    )

def main(count=300):
    init_db()
    db = SessionLocal()
    base_time = datetime.utcnow()

    events = [generate_event(base_time) for _ in range(count)]
    db.add_all(events)
    db.commit()
    db.close()

    print(f"Inserted {count} fake events.")

if __name__ == "__main__":
    main()
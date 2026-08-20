import sys
import os
import time
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models import Event

def lookup_ip(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = resp.json()
        if data.get("status") == "success":
            return {
                "country": data.get("country"),
                "city": data.get("city"),
                "latitude": data.get("lat"),
                "longitude": data.get("lon"),
            }
    except requests.RequestException:
        pass
    return None

def main():
    db = SessionLocal()

    # Get unique IPs that haven't been enriched yet
    unenriched = (
        db.query(Event.src_ip)
        .filter(Event.country.is_(None))
        .distinct()
        .all()
    )
    unique_ips = [row[0] for row in unenriched if row[0]]

    print(f"Found {len(unique_ips)} unique IPs to enrich.")

    ip_cache = {}
    for ip in unique_ips:
        geo = lookup_ip(ip)
        if geo:
            ip_cache[ip] = geo
            print(f"{ip} -> {geo['city']}, {geo['country']}")
        else:
            print(f"{ip} -> lookup failed")
        time.sleep(1.5)  # stay well under 45 req/min rate limit

    # Apply enrichment to all matching events
    updated = 0
    for ip, geo in ip_cache.items():
        events = db.query(Event).filter(Event.src_ip == ip).all()
        for event in events:
            event.country = geo["country"]
            event.city = geo["city"]
            event.latitude = geo["latitude"]
            event.longitude = geo["longitude"]
            updated += 1

    db.commit()
    db.close()
    print(f"Updated {updated} events with geolocation data.")

if __name__ == "__main__":
    main()
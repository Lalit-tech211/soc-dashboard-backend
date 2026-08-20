from fastapi import FastAPI
from app.database import init_db, SessionLocal
from app.models import Event

app = FastAPI(title="SOC Dashboard API")
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SOC Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"status": "SOC Dashboard API is running"}

@app.get("/events")
def get_events():
    db = SessionLocal()
    events = db.query(Event).all()
    db.close()
    return events
from sqlalchemy import func

@app.get("/stats/summary")
def get_summary():
    db = SessionLocal()
    total_events = db.query(Event).count()
    unique_ips = db.query(Event.src_ip).distinct().count()
    login_attempts = db.query(Event).filter(Event.event_id.like("%login%")).count()
    db.close()
    return {
        "total_events": total_events,
        "unique_ips": unique_ips,
        "login_attempts": login_attempts,
    }

@app.get("/stats/top-usernames")
def get_top_usernames():
    db = SessionLocal()
    results = (
        db.query(Event.username, func.count(Event.id).label("count"))
        .filter(Event.username.isnot(None))
        .group_by(Event.username)
        .order_by(func.count(Event.id).desc())
        .limit(10)
        .all()
    )
    db.close()
    return [{"username": r[0], "count": r[1]} for r in results]

@app.get("/stats/locations")
def get_locations():
    db = SessionLocal()
    results = (
        db.query(Event.src_ip, Event.city, Event.country, Event.latitude, Event.longitude)
        .filter(Event.latitude.isnot(None))
        .distinct()
        .all()
    )
    db.close()
    return [
        {"src_ip": r[0], "city": r[1], "country": r[2], "latitude": r[3], "longitude": r[4]}
        for r in results
    ]
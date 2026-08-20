from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, index=True)          # e.g. cowrie.login.failed
    session_id = Column(String, index=True)
    src_ip = Column(String, index=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # geolocation enrichment
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
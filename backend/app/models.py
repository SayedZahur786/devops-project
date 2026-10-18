from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, String, Text

from .database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    team_name = Column(String(120), nullable=False)
    hackathon = Column(String(120), nullable=False)
    track = Column(String(120), nullable=False, default="open")
    status = Column(String(20), nullable=False, default="idea")  # idea | building | submitted | won
    priority = Column(String(10), nullable=False, default="medium")  # low | medium | high
    description = Column(Text, nullable=True)
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class LocationModel(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = ""


class CrimeReportCreate(BaseModel):
    category: str  # চাঁদাবাজি, চুরি, ডাকাতি, হয়রানি, মাদক, হামলা, সন্দেহজনক
    description: str
    location: LocationModel
    incident_time: datetime
    is_anonymous: bool = True
    evidence_urls: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "category": "চাঁদাবাজি",
                "description": "একটি দোকানে ৩ জন এসে চাঁদা দাবি করে।",
                "location": {"lat": 23.7461, "lng": 90.3742, "name": "মিরপুর ১০"},
                "incident_time": "2026-03-11T20:30:00",
                "is_anonymous": True,
                "evidence_urls": [],
            }
        }


class VoteModel(BaseModel):
    vote_type: str  # "up" or "down"


class CrimeReportOut(BaseModel):
    id: str
    category: str
    description: str
    location: LocationModel
    incident_time: datetime
    is_anonymous: bool
    reporter_id: Optional[str] = None
    reporter_name: Optional[str] = None
    evidence_urls: List[str] = []
    upvotes: int = 0
    downvotes: int = 0
    trust_score: float = 0.0
    status: str = "active"
    notes_count: int = 0
    created_at: datetime
    user_vote: Optional[str] = None  # "up", "down", or None


class HeatmapPoint(BaseModel):
    lat: float
    lng: float
    weight: float
    category: str

# ----- REQUIRED IMPORTS -----

from pydantic import BaseModel
from typing import List, Dict, Optional

# ----- CLASS DEFINITIONS -----

class UserCredentials(BaseModel):
    """SMU credentials storage model"""
    email: str
    password: str

    def json(self, **kwargs):
        return super().json(exclude={'password'}, **kwargs)

class ScrapeRequest(BaseModel):
    """Scraping parameters model"""
    buildings: List[str]
    floors: List[str]
    facility_types: List[str]
    equipment: List[str]
    email: str
    password: str

class ScrapeResult(BaseModel):
    """Scraping results container"""
    status: str  # 'success' or 'error'
    data: Optional[Dict[str, List[Dict[str, str]]]]  # Room -> Timeslots
    message: Optional[str]  # Error message
    errors: List[str] = []

class TimeSlot(BaseModel):
    """Individual timeslot availability"""
    start: str
    end: str
    status: str  # Available/Booked
    equipment: List[str]

class RoomAvailability(BaseModel):
    """Complete room availability data"""
    room_number: str
    capacity: int
    type: str
    equipment: List[str]
    timeslots: List[TimeSlot]

class APIScrapeResponse(BaseModel):
    """API response format"""
    task_id: str
    status_url: str
    status: str
    result: Optional[List[RoomAvailability]]
    error: Optional[str]

class TelegramScrapeResponse(BaseModel):
    """Telegram-optimized response format"""
    success: bool
    summary: str
    details: List[str]
    errors: List[str]
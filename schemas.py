"""
Database Schemas for RSCOE E-Club E-Summit

Each Pydantic model corresponds to one MongoDB collection (lowercased class name).
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class Speaker(BaseModel):
    name: str = Field(..., description="Speaker full name")
    title: Optional[str] = Field(None, description="Role/Title")
    company: Optional[str] = Field(None, description="Company/Org")
    bio: Optional[str] = Field(None, description="Short bio")
    photo_url: Optional[str] = Field(None, description="Image URL")
    socials: Optional[dict] = Field(default_factory=dict, description="Social links")

class Event(BaseModel):
    name: str = Field(..., description="Event name")
    description: Optional[str] = Field(None, description="Event description")
    date: datetime = Field(..., description="Event date & time (UTC)")
    location: str = Field(..., description="Venue or online link")
    speaker_ids: List[str] = Field(default_factory=list, description="Related speaker IDs")
    price: float = Field(0.0, ge=0, description="Ticket price in INR")
    capacity: Optional[int] = Field(None, ge=0, description="Max seats")
    tags: List[str] = Field(default_factory=list)

class TicketOrder(BaseModel):
    event_id: str = Field(..., description="Event ID")
    buyer_name: str = Field(..., description="Buyer full name")
    buyer_email: EmailStr
    quantity: int = Field(..., ge=1, le=10)
    amount_paid: float = Field(0.0, ge=0, description="Amount paid in INR")
    status: str = Field("pending", description="pending, confirmed, cancelled")

class Highlight(BaseModel):
    year: int = Field(..., description="Year of the summit")
    headline: str
    stats: dict = Field(default_factory=dict)
    gallery: List[str] = Field(default_factory=list, description="Image URLs")

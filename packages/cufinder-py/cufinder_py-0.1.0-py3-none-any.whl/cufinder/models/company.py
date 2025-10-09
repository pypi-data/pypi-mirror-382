"""Company-related data models."""

from typing import List, Optional

from .base import BaseModel


class Company(BaseModel):
    """Company information model."""
    
    name: Optional[str] = None
    domain: Optional[str] = None
    linkedin_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    founded: Optional[int] = None
    revenue: Optional[str] = None
    employees: Optional[dict] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    social_media: Optional[dict] = None
    technologies: Optional[List[str]] = None
    subsidiaries: Optional[List[str]] = None
    headquarters: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    address: Optional[str] = None

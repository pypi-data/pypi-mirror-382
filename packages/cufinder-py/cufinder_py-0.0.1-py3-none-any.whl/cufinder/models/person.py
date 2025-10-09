"""Person-related data models."""

from typing import List, Optional

from .base import BaseModel


class Person(BaseModel):
    """Person information model."""
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    company_domain: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    experience: Optional[List[dict]] = None
    education: Optional[List[dict]] = None
    skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    social_media: Optional[dict] = None

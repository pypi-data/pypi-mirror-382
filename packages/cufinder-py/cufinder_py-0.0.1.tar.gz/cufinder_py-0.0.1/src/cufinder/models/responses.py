"""API response models."""

from typing import List, Optional

from .base import BaseModel
from .company import Company
from .person import Person


class MetaData(BaseModel):
    """Metadata for API responses."""
    user_id: Optional[int] = None
    service_name: Optional[str] = None
    spent_time: Optional[float] = None
    status_code: Optional[int] = None
    message: Optional[str] = None
    query_log: Optional[str] = None


class BaseResponse(BaseModel):
    """Base response model for all CUFinder API responses."""
    query: Optional[str] = None
    credit_count: Optional[int] = None
    meta_data: Optional[MetaData] = None
    confidence_level: Optional[int] = None


class CufResponse(BaseResponse):
    """Response model for CUF (Company URL Finder) API."""
    
    domain: Optional[str] = None


class LcufResponse(BaseResponse):
    """Response model for LCUF (LinkedIn Company URL Finder) API."""
    
    linkedin_url: Optional[str] = None


class DtcResponse(BaseResponse):
    """Response model for DTC (Domain to Company Name) API."""
    
    company_name: Optional[str] = None


class DteResponse(BaseResponse):
    """Response model for DTE (Company Email Finder) API."""
    
    emails: Optional[List[str]] = None


class NtpResponse(BaseResponse):
    """Response model for NTP (Company Phone Finder) API."""
    
    phones: Optional[List[str]] = None


class RelResponse(BaseResponse):
    """Response model for REL (Reverse Email Lookup) API."""
    
    person: Optional[Person] = None


class FclResponse(BaseResponse):
    """Response model for FCL (Company Lookalikes Finder) API."""
    
    companies: Optional[List[dict]] = None


class ElfResponse(BaseResponse):
    """Response model for ELF (Company Fundraising) API."""
    
    fundraising_info: Optional[dict] = None


class CarResponse(BaseResponse):
    """Response model for CAR (Company Revenue Finder) API."""
    
    annual_revenue: Optional[str] = None


class FccResponse(BaseResponse):
    """Response model for FCC (Company Subsidiaries Finder) API."""
    
    subsidiaries: Optional[List[str]] = None


class FtsResponse(BaseResponse):
    """Response model for FTS (Company Tech Stack Finder) API."""
    
    technologies: Optional[List[str]] = None


class EppResponse(BaseResponse):
    """Response model for EPP (LinkedIn Profile Enrichment) API."""
    
    person: Optional[Person] = None


class FweResponse(BaseResponse):
    """Response model for FWE (LinkedIn Profile Email Finder) API."""
    
    work_email: Optional[str] = None


class TepResponse(BaseResponse):
    """Response model for TEP (Person Enrichment) API."""
    
    person: Optional[Person] = None


class EncResponse(BaseResponse):
    """Response model for ENC (Company Enrichment) API."""
    
    company: Optional[Company] = None


class CecResponse(BaseResponse):
    """Response model for CEC (Company Employee Countries) API."""
    
    countries: Optional[dict] = None


class CloResponse(BaseResponse):
    """Response model for CLO (Company Locations) API."""
    
    locations: Optional[List[dict]] = None


class CseResponse(BaseResponse):
    """Response model for CSE (Company Search) API."""
    
    companies: Optional[List[dict]] = None


class PseResponse(BaseResponse):
    """Response model for PSE (People Search) API."""
    
    peoples: Optional[List[dict]] = None


class LbsResponse(BaseResponse):
    """Response model for LBS (Local Business Search) API."""
    
    companies: Optional[List[dict]] = None

"""EPP - Email Pattern Predictor service."""

from ..models.responses import EppResponse
from .base import BaseService


class Epp(BaseService):
    """
    EPP - LinkedIn Profile Enrichment API (V2).
    
    Takes a LinkedIn profile URL and returns enriched person and company data.
    """

    def enrich_profile(self, linkedin_url: str) -> EppResponse:
        """
        Enrich LinkedIn profile.
        
        Args:
            linkedin_url: The LinkedIn profile URL to enrich
            
        Returns:
            EppResponse: Enriched person and company data
        """
        try:
            response_data = self.client.post("/epp", {
                "linkedin_url": linkedin_url.strip(),
            })

            return self.parse_response(response_data, EppResponse)
        except Exception as error:
            raise self.handle_error(error, "EPP Service")

"""LBS - Local Business Search service."""

from typing import Dict, Any, Optional

from ..models.responses import LbsResponse
from .base import BaseService


class Lbs(BaseService):
    """
    LBS - Local Business Search API (V2).
    
    Search for local businesses by location, industry, or name.
    """

    def search_local_businesses(
        self,
        name: Optional[str] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        industry: Optional[str] = None,
        page: Optional[int] = None,
    ) -> LbsResponse:
        """
        Search local businesses.
        
        Args:
            name: Business name to search for
            country: Country to search in
            state: State/Province to search in
            city: City to search in
            industry: Industry to filter by
            page: Page number for pagination
            
        Returns:
            LbsResponse: Local business search results
        """
        try:
            search_params: Dict[str, Any] = {}

            # Add non-None parameters
            if name is not None:
                search_params["name"] = name
            if country is not None:
                search_params["country"] = country
            if state is not None:
                search_params["state"] = state
            if city is not None:
                search_params["city"] = city
            if industry is not None:
                search_params["industry"] = industry
            if page is not None:
                search_params["page"] = page

            response_data = self.client.post("/lbs", search_params)

            return self.parse_response(response_data, LbsResponse)
        except Exception as error:
            raise self.handle_error(error, "LBS Service")

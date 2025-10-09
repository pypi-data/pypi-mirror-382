"""CLO - Company Locations service."""

from ..models.responses import CloResponse
from .base import BaseService


class Clo(BaseService):
    """
    CLO - Company Locations API (V2).
    
    Returns office locations for a company.
    """

    def get_locations(self, query: str) -> CloResponse:
        """
        Get company locations.
        
        Args:
            query: Company name to get locations for
            
        Returns:
            CloResponse: Company locations information
            
        Example:
            ```python
            locations = sdk.clo("TechCorp")
            print(f"Found {locations.total} office locations")
            ```
        """

        try:
            response_data = self.client.post("/clo", {
                "query": query.strip(),
            })

            return self.parse_response(response_data, CloResponse)
        except Exception as error:
            raise self.handle_error(error, "CLO Service")

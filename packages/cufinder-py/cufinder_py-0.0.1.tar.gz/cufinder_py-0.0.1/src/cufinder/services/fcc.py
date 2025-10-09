"""FCC - Company Subsidiaries Finder service."""

from ..models.responses import FccResponse
from .base import BaseService


class Fcc(BaseService):
    """
    FCC - Company Subsidiaries Finder API (V2).
    
    Identifies known subsidiaries of a parent company.
    """

    def get_subsidiaries(self, query: str) -> FccResponse:
        """
        Get company subsidiaries.
        
        Args:
            query: Company name to find subsidiaries for
            
        Returns:
            FccResponse: Subsidiaries information
            
        Example:
            ```python
            subsidiaries = sdk.fcc("Alphabet Inc")
            print(f"Found {subsidiaries.total} subsidiaries")
            ```
        """

        try:
            response_data = self.client.post("/fcc", {
                "query": query.strip(),
            })

            return self.parse_response(response_data, FccResponse)
        except Exception as error:
            raise self.handle_error(error, "FCC Service")

"""FCL - Company Lookalikes Finder service."""

from ..models.responses import FclResponse
from .base import BaseService


class Fcl(BaseService):
    """
    FCL - Company Lookalikes Finder API (V2).
    
    Provides a list of similar companies based on an input company's profile.
    """

    def get_lookalikes(self, query: str) -> FclResponse:
        """
        Get company lookalikes.
        
        Args:
            query: Company name or description to find similar companies for
            
        Returns:
            FclResponse: List of similar companies
            
        Example:
            ```python
            lookalikes = sdk.fcl("TechCorp")
            print(f"Found {lookalikes.total} similar companies")
            ```
        """

        try:
            response_data = self.client.post("/fcl", {
                "query": query.strip(),
            })

            return self.parse_response(response_data, FclResponse)
        except Exception as error:
            raise self.handle_error(error, "FCL Service")

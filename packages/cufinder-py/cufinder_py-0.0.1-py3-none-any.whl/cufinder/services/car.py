"""CAR - Company Revenue Finder service."""

from ..models.responses import CarResponse
from .base import BaseService


class Car(BaseService):
    """
    CAR - Company Revenue Finder API (V2).
    
    Estimates a company's annual revenue based on name.
    """

    def get_revenue(self, query: str) -> CarResponse:
        """
        Get company revenue.
        
        Args:
            query: Company name to get revenue data for
            
        Returns:
            CarResponse: Revenue information
            
        Example:
            ```python
            revenue = sdk.car("TechCorp")
            print(revenue.revenue)  # '$50M - $100M'
            ```
        """

        try:
            response_data = self.client.post("/car", {
                "query": query.strip(),
            })

            return self.parse_response(response_data, CarResponse)
        except Exception as error:
            raise self.handle_error(error, "CAR Service")

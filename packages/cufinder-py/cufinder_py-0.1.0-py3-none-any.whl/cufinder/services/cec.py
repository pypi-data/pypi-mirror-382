"""CEC - Company Employee Countries service."""

from ..models.responses import CecResponse
from .base import BaseService


class Cec(BaseService):
    """
    CEC - Company Employee Countries API (V2).
    
    Returns countries where a company has employees.
    """

    def get_employee_countries(self, query: str) -> CecResponse:
        """
        Get company employee countries.
        
        Args:
            query: Company name to get employee countries for
            
        Returns:
            CecResponse: Employee countries information
            
        Example:
            ```python
            countries = sdk.cec("TechCorp")
            print(countries.countries)  # ['United States', 'Canada', 'UK']
            ```
        """

        try:
            response_data = self.client.post("/cec", {
                "query": query.strip(),
            })

            return self.parse_response(response_data, CecResponse)
        except Exception as error:
            raise self.handle_error(error, "CEC Service")

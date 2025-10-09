"""CUF - Company URL Finder service."""

from ..models.responses import CufResponse
from .base import BaseService


class Cuf(BaseService):
    """
    CUF - Company Name to Domain API.
    
    Returns the official website URL of a company based on its name.
    """

    def get_domain(
        self,
        company_name: str,
        country_code: str,
    ) -> CufResponse:
        """
        Get company domain from company name.
        
        Args:
            company_name: The name of the company
            country_code: ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')
            
        Returns:
            CufResponse: Company domain information
            
        Example:
            ```python
            domain = await sdk.cuf(
                company_name="TechCorp",
                country_code="US"
            )
            print(domain.domain)  # 'techcorp.com'
            ```
        """

        try:
            response_data = self.client.post("/cuf", {
                "company_name": company_name.strip(),
                "country_code": country_code.strip().upper(),
            })

            return self.parse_response(response_data, CufResponse)
        except Exception as error:
            raise self.handle_error(error, "CUF Service")

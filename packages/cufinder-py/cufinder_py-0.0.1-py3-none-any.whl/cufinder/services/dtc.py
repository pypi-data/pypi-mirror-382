"""DTC - Domain to Company Name service."""

from ..models.responses import DtcResponse
from .base import BaseService


class Dtc(BaseService):
    """
    DTC - Domain to Company Name API (V2).
    
    Retrieves the registered company name associated with a given website domain.
    """

    def get_company_name(self, company_website: str) -> DtcResponse:
        """
        Get company name from domain.
        
        Args:
            company_website: The website URL to lookup
            
        Returns:
            DtcResponse: Company name information
            
        Example:
            ```python
            company = sdk.dtc("https://example.com")
            print(company.company_name)  # 'Example Corp'
            ```
        """
        try:
            response_data = self.client.post("/dtc", {
                "company_website": company_website.strip(),
            })

            return self.parse_response(response_data, DtcResponse)
        except Exception as error:
            raise self.handle_error(error, "DTC Service")

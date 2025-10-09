"""LCUF - LinkedIn Company URL Finder service."""

from ..models.responses import LcufResponse
from .base import BaseService


class Lcuf(BaseService):
    """
    LCUF - LinkedIn Company URL Finder API (V2).
    
    Finds LinkedIn company URLs from company names.
    """

    def get_linkedin_url(self, company_name: str) -> LcufResponse:
        """
        Get LinkedIn URL from company name.
        
        Args:
            company_name: The name of the company to find LinkedIn URL for
            
        Returns:
            LcufResponse: LinkedIn URL information
            
        Example:
            ```python
            linkedin = sdk.lcuf("TechCorp")
            print(linkedin.linkedin_url)  # 'https://linkedin.com/company/techcorp'
            ```
        """

        try:
            response_data = self.client.post("/lcuf", {
                "company_name": company_name.strip(),
            })

            return self.parse_response(response_data, LcufResponse)
        except Exception as error:
            raise self.handle_error(error, "LCUF Service")

"""DTE - Company Email Finder service."""

from ..models.responses import DteResponse
from .base import BaseService


class Dte(BaseService):
    """
    DTE - Company Email Finder API (V2).
    
    Returns up to five general or role-based business email addresses for a company.
    """

    def get_emails(self, company_website: str) -> DteResponse:
        """
        Get company emails from domain.
        
        Args:
            company_website: The website URL to find emails for
            
        Returns:
            DteResponse: Company email information
            
        Example:
            ```python
            emails = sdk.dte("https://example.com")
            print(emails.emails)  # ['contact@example.com', 'info@example.com']
            ```
        """
        try:
            response_data = self.client.post("/dte", {
                "company_website": company_website.strip(),
            })

            return self.parse_response(response_data, DteResponse)
        except Exception as error:
            raise self.handle_error(error, "DTE Service")


__all__ = ["Dte"]

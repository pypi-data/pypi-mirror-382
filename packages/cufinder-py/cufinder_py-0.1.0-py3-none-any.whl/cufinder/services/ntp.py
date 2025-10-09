"""NTP - Company Phone Finder service."""

from ..models.responses import NtpResponse
from .base import BaseService


class Ntp(BaseService):
    """
    NTP - Company Phone Finder API (V2).
    
    Returns up to two verified phone numbers for a company.
    """

    def get_phones(self, company_name: str) -> NtpResponse:
        """
        Get company phones from company name.
        
        Args:
            company_name: The name of the company to find phones for
            
        Returns:
            NtpResponse: Company phone information
            
        Example:
            ```python
            phones = sdk.ntp("TechCorp")
            print(phones.phones)  # ['+1-555-123-4567', '+1-555-987-6543']
            ```
        """

        try:
            response_data = self.client.post("/ntp", {
                "company_name": company_name.strip(),
            })

            return self.parse_response(response_data, NtpResponse)
        except Exception as error:
            raise self.handle_error(error, "NTP Service")

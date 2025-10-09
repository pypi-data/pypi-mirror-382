"""ELF - Company Fundraising service."""

from ..models.responses import ElfResponse
from .base import BaseService


class Elf(BaseService):
    """
    ELF - Company Fundraising API (V2).
    
    Returns detailed funding information about a company.
    """

    def get_fundraising(self, query: str) -> ElfResponse:
        """
        Get company fundraising information.
        
        Args:
            query: Company name to get fundraising data for
            
        Returns:
            ElfResponse: Fundraising information
            
        Example:
            ```python
            funding = sdk.elf("TechCorp")
            print(funding.fundraising)  # {'total_raised': '$10M', 'rounds': [...]}
            ```
        """

        try:
            response_data = self.client.post("/elf", {
                "query": query.strip(),
            })

            return self.parse_response(response_data, ElfResponse)
        except Exception as error:
            raise self.handle_error(error, "ELF Service")

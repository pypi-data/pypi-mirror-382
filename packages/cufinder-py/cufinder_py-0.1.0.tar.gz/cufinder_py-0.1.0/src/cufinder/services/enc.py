"""ENC - Company Enrichment service."""

from ..models.responses import EncResponse
from .base import BaseService


class Enc(BaseService):
    """
    ENC - Company Enrichment API (V2).
    
    Enriches company information from various data sources.
    """

    def enrich_company(self, query: str) -> EncResponse:
        """
        Enrich company information.
        
        Args:
            query: Company name or domain to enrich
            
        Returns:
            EncResponse: Enriched company information
            
        Example:
            ```python
            company = sdk.enc("TechCorp")
            print(company.company.name)  # 'TechCorp Inc'
            print(company.company.industry)  # 'Technology'
            ```
        """

        try:
            response_data = self.client.post("/enc", {
                "query": query.strip(),
            })

            return self.parse_response(response_data, EncResponse)
        except Exception as error:
            raise self.handle_error(error, "ENC Service")

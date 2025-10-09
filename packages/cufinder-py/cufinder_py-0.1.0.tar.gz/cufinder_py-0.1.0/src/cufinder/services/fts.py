"""FTS - Company Tech Stack Finder service."""

from ..models.responses import FtsResponse
from .base import BaseService


class Fts(BaseService):
    """
    FTS - Company Tech Stack Finder API (V2).
    
    Returns technology stack information for a company.
    """

    def get_tech_stack(self, query: str) -> FtsResponse:
        """
        Get company tech stack.
        
        Args:
            query: Company name or website to get tech stack for
            
        Returns:
            FtsResponse: Technology stack information
            
        Example:
            ```python
            tech_stack = sdk.fts("TechCorp")
            print(tech_stack.tech_stack)  # ['Python', 'React', 'AWS', ...]
            ```
        """

        try:
            response_data = self.client.post("/fts", {
                "query": query.strip(),
            })

            return self.parse_response(response_data, FtsResponse)
        except Exception as error:
            raise self.handle_error(error, "FTS Service")

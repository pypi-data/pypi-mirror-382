"""REL - Reverse Email Lookup service."""


from ..models.responses import RelResponse
from .base import BaseService


class Rel(BaseService):
    """
    REL - Reverse Email Lookup API (V2).
    
    Enriches an email address with detailed person and company information.
    """

    def reverse_email_lookup(self, email: str) -> RelResponse:
        """
        Reverse email lookup.
        
        Args:
            email: The email address to lookup
            
        Returns:
            RelResponse: Person and company information
            
        Example:
            ```python
            person = sdk.rel("john.doe@example.com")
            print(person.person.full_name)  # 'John Doe'
            print(person.company.name)  # 'Example Corp'
            ```
        """


        try:
            response_data = self.client.post("/rel", {
                "email": email.strip(),
            })

            return self.parse_response(response_data, RelResponse)
        except Exception as error:
            raise self.handle_error(error, "REL Service")

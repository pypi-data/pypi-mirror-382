"""FWE - Email from Profile service."""


from ..models.responses import FweResponse
from .base import BaseService


class Fwe(BaseService):
    """
    FWE - Email from Profile API (V2).
    
    Extracts email addresses from social media profiles.
    """

    def get_email_from_profile(self, profile_url: str) -> FweResponse:
        """
        Get email from profile.
        
        Args:
            profile_url: Social media profile URL to extract email from
            
        Returns:
            FweResponse: Email information
            
        Example:
            ```python
            email = sdk.fwe("https://linkedin.com/in/johndoe")
            print(email.email)  # 'john.doe@example.com'
            ```
        """
        try:
            response_data = self.client.post("/fwe", {
                "linkedin_url": profile_url.strip(),
            })

            return self.parse_response(response_data, FweResponse)
        except Exception as error:
            raise self.handle_error(error, "FWE Service")

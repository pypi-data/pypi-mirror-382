"""Base service class for all Cufinder API services."""

from ..client import CufinderClient
from ..exceptions import CufinderError


class BaseService:
    """
    Base service class that provides common functionality for all services.
    
    Follows SOLID principles by providing a single responsibility base class.
    """

    def __init__(self, client: CufinderClient):
        """
        Initialize the base service.
        
        Args:
            client: The CufinderClient instance
        """
        self.client = client

    def parse_response(self, response_data: dict, response_class):
        """
        Parse API response with data wrapper.
        
        Args:
            response_data: Raw API response
            response_class: Response model class
            
        Returns:
            Parsed response model
        """
        if "data" in response_data:
            data = response_data["data"]
            # The data object already contains query, credit_count, etc.
            if "meta_data" in response_data:
                data["meta_data"] = response_data["meta_data"]
            return response_class.from_dict(data)
        else:
            return response_class.from_dict(response_data)


    def handle_error(self, error: Exception, service_name: str) -> CufinderError:
        """
        Handle service errors consistently.
        
        Args:
            error: The error to handle
            service_name: The name of the service for error context
            
        Returns:
            CufinderError: Formatted error
        """
        if isinstance(error, CufinderError):
            return error

        # Handle other exceptions
        return CufinderError(
            f"{service_name}: {str(error)}",
            "UNKNOWN_ERROR",
            500,
        )


__all__ = ["BaseService"]
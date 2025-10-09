"""CSE - Company Search service."""

from typing import Optional

from ..models.responses import CseResponse
from .base import BaseService


class Cse(BaseService):
    """
    CSE - Company Search API (V2).
    
    Search for companies based on various criteria.
    """

    def search_companies(
        self,
        name: Optional[str] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        followers_count_min: Optional[int] = None,
        followers_count_max: Optional[int] = None,
        industry: Optional[str] = None,
        employee_size: Optional[str] = None,
        founded_after_year: Optional[int] = None,
        founded_before_year: Optional[int] = None,
        funding_amount_max: Optional[int] = None,
        funding_amount_min: Optional[int] = None,
        products_services: Optional[list] = None,
        is_school: Optional[bool] = None,
        annual_revenue_min: Optional[int] = None,
        annual_revenue_max: Optional[int] = None,
        page: Optional[int] = None,
    ) -> CseResponse:
        """
        Search companies.
        
        Args:
            name: Company name to search for
            country: Country to filter by
            state: State/Province to filter by
            city: City to filter by
            followers_count_min: Minimum followers count
            followers_count_max: Maximum followers count
            industry: Industry to filter by
            employee_size: Employee size to filter by
            founded_after_year: Founded after year
            founded_before_year: Founded before year
            funding_amount_max: Maximum funding amount
            funding_amount_min: Minimum funding amount
            products_services: List of products/services
            is_school: Filter for schools only
            annual_revenue_min: Minimum annual revenue
            annual_revenue_max: Maximum annual revenue
            page: Page number for pagination
            
        Returns:
            CseResponse: Company search results
            
        Example:
            ```python
            companies = sdk.cse(name="technology", country="US", industry="software")
            print(f"Found {companies.total} companies")
            ```
        """
        try:
            search_params = {}

            # Add non-None parameters
            if name is not None:
                search_params["name"] = name
            if country is not None:
                search_params["country"] = country
            if state is not None:
                search_params["state"] = state
            if city is not None:
                search_params["city"] = city
            if followers_count_min is not None:
                search_params["followers_count_min"] = followers_count_min
            if followers_count_max is not None:
                search_params["followers_count_max"] = followers_count_max
            if industry is not None:
                search_params["industry"] = industry
            if employee_size is not None:
                search_params["employee_size"] = employee_size
            if founded_after_year is not None:
                search_params["founded_after_year"] = founded_after_year
            if founded_before_year is not None:
                search_params["founded_before_year"] = founded_before_year
            if funding_amount_max is not None:
                search_params["funding_amount_max"] = funding_amount_max
            if funding_amount_min is not None:
                search_params["funding_amount_min"] = funding_amount_min
            if products_services is not None:
                search_params["products_services"] = products_services
            if is_school is not None:
                search_params["is_school"] = is_school
            if annual_revenue_min is not None:
                search_params["annual_revenue_min"] = annual_revenue_min
            if annual_revenue_max is not None:
                search_params["annual_revenue_max"] = annual_revenue_max
            if page is not None:
                search_params["page"] = page

            response_data = self.client.post("/cse", search_params)

            return self.parse_response(response_data, CseResponse)
        except Exception as error:
            raise self.handle_error(error, "CSE Service")

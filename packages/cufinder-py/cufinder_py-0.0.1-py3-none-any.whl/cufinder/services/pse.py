"""PSE - People Search service."""

from typing import Optional

from ..models.responses import PseResponse
from .base import BaseService


class Pse(BaseService):
    """
    PSE - People Search API (V2).
    
    Search for people based on various criteria.
    """

    def search_people(
        self,
        full_name: Optional[str] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        job_title_role: Optional[str] = None,
        job_title_level: Optional[str] = None,
        company_country: Optional[str] = None,
        company_state: Optional[str] = None,
        company_city: Optional[str] = None,
        company_name: Optional[str] = None,
        company_linkedin_url: Optional[str] = None,
        company_industry: Optional[str] = None,
        company_employee_size: Optional[str] = None,
        company_products_services: Optional[list] = None,
        company_annual_revenue_min: Optional[int] = None,
        company_annual_revenue_max: Optional[int] = None,
        page: Optional[int] = None,
    ) -> PseResponse:
        """
        Search people.
        
        Args:
            full_name: Full name to search for
            country: Country to filter by
            state: State/Province to filter by
            city: City to filter by
            job_title_role: Job title role to filter by
            job_title_level: Job title level to filter by
            company_country: Company country to filter by
            company_state: Company state to filter by
            company_city: Company city to filter by
            company_name: Company name to filter by
            company_linkedin_url: Company LinkedIn URL to filter by
            company_industry: Company industry to filter by
            company_employee_size: Company employee size to filter by
            company_products_services: Company products/services to filter by
            company_annual_revenue_min: Company minimum annual revenue
            company_annual_revenue_max: Company maximum annual revenue
            page: Page number for pagination
            
        Returns:
            PseResponse: People search results
            
        Example:
            ```python
            people = sdk.pse(full_name="John", company_name="TechCorp", job_title_role="Engineer")
            print(f"Found {people.total} people")
            ```
        """
        try:
            search_params = {}

            # Add non-None parameters
            if full_name is not None:
                search_params["full_name"] = full_name
            if country is not None:
                search_params["country"] = country
            if state is not None:
                search_params["state"] = state
            if city is not None:
                search_params["city"] = city
            if job_title_role is not None:
                search_params["job_title_role"] = job_title_role
            if job_title_level is not None:
                search_params["job_title_level"] = job_title_level
            if company_country is not None:
                search_params["company_country"] = company_country
            if company_state is not None:
                search_params["company_state"] = company_state
            if company_city is not None:
                search_params["company_city"] = company_city
            if company_name is not None:
                search_params["company_name"] = company_name
            if company_linkedin_url is not None:
                search_params["company_linkedin_url"] = company_linkedin_url
            if company_industry is not None:
                search_params["company_industry"] = company_industry
            if company_employee_size is not None:
                search_params["company_employee_size"] = company_employee_size
            if company_products_services is not None:
                search_params["company_products_services"] = company_products_services
            if company_annual_revenue_min is not None:
                search_params["company_annual_revenue_min"] = company_annual_revenue_min
            if company_annual_revenue_max is not None:
                search_params["company_annual_revenue_max"] = company_annual_revenue_max
            if page is not None:
                search_params["page"] = page

            response_data = self.client.post("/pse", search_params)

            return self.parse_response(response_data, PseResponse)
        except Exception as error:
            raise self.handle_error(error, "PSE Service")

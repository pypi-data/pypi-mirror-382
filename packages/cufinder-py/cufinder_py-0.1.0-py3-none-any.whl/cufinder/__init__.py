"""
Cufinder Python SDK - Type-safe Python SDK for the Cufinder B2B Data Enrichment API

Example:
    ```python
    from cufinder import CufinderSDK
    
    sdk = CufinderSDK(api_key="your-api-key-here")
    
    # API usage
    company = await sdk.cuf(
        company_name="TechCorp",
        country_code="US"
    )
    print(company.domain)  # 'techcorp.com'
    ```
"""

from .client import CufinderClient
from .sdk import CufinderSDK
from .exceptions import (
    CufinderError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    CreditLimitError,
    NetworkError,
)
from .models import *
from .services import *

__version__ = "0.1.0"
__author__ = "CUFinder Team"
__email__ = "support@cufinder.io"

# SDK metadata
SDK_INFO = {
    "name": "cufinder-py",
    "version": __version__,
    "description": "Type-safe Python SDK for the CUFinder B2B Data Enrichment API",
    "homepage": "https://github.com/cufinder/cufinder-py",
    "repository": "https://github.com/cufinder/cufinder-py.git",
    "author": __author__,
    "license": "MIT",
}

__all__ = [
    "CufinderSDK",
    "CufinderClient",
    "CufinderError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "CreditLimitError",
    "NetworkError",
    # Models
    "BaseModel",
    "Company",
    "Person",
    "CufResponse",
    "EppResponse", 
    "LbsResponse",
    "DtcResponse",
    "DteResponse",
    "NtpResponse",
    "RelResponse",
    "FclResponse",
    "ElfResponse",
    "CarResponse",
    "FccResponse",
    "FtsResponse",
    "FweResponse",
    "TepResponse",
    "EncResponse",
    "CecResponse",
    "CloResponse",
    "CseResponse",
    "PseResponse",
    "LcufResponse",
    # Services
    "BaseService",
    "Cuf",
    "Epp", 
    "Lbs",
    "Dtc",
    "Dte",
    "Ntp",
    "Rel",
    "Fcl",
    "Elf",
    "Car",
    "Fcc",
    "Fts",
    "Fwe",
    "Tep",
    "Enc",
    "Cec",
    "Clo",
    "Cse",
    "Pse",
    "Lcuf",
    "__version__",
    "SDK_INFO",
]

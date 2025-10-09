# CUFinder Python SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/cufinder-py.svg)](https://badge.fury.io/py/cufinder-py)

Type-safe Python SDK for easily integrating with the CUFinder B2B Data Enrichment API.

## Features

- 🚀 **Type-safe**: Built with Pydantic for full type safety and validation
- 🔧 **Easy to use**: Simple, intuitive API design
- 🛡️ **Robust**: Comprehensive error handling and retry logic
- 📚 **Well documented**: Extensive documentation and examples
- 🔄 **Async ready**: Built for both sync and async usage patterns
- 🎯 **Production ready**: Battle-tested in production environments

## Installation

```bash
pip install cufinder-py
```

## Quick Start

```python
from cufinder import CufinderSDK

# Initialize the SDK
sdk = CufinderSDK(api_key="your-api-key-here")

# Get company domain from company name
company = sdk.cuf(
    company_name="TechCorp",
    country_code="US"
)
print(company.domain)  # 'techcorp.com'

# Enrich LinkedIn profile
profile = sdk.epp(
    linkedin_url="https://linkedin.com/in/johndoe"
)
print(profile.person.full_name)  # 'John Doe'

# Search local businesses
businesses = sdk.lbs(
    name="coffee shop",
    city="San Francisco",
    state="CA"
)
print(f"Found {businesses.total} businesses")
```

## API Services

### CUF - Company URL Finder
Find the official website URL of a company based on its name.

```python
domain = sdk.cuf(
    company_name="Microsoft",
    country_code="US"
)
```

### EPP - Email Pattern Predictor
Enrich LinkedIn profiles to get person and company data.

```python
profile = sdk.epp(
    linkedin_url="https://linkedin.com/in/satyanadella"
)
```

### LBS - Local Business Search
Search for local businesses by location, industry, or name.

```python
businesses = sdk.lbs(
    name="restaurant",
    city="New York",
    state="NY",
    industry="food"
)
```

## Configuration

```python
sdk = CufinderSDK(
    api_key="your-api-key",
    base_url="https://api.cufinder.io/v2",  # Optional
    timeout=30,  # Optional, default 30 seconds
    max_retries=3  # Optional, default 3 retries
)
```

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

```python
from cufinder import (
    CufinderError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    CreditLimitError,
    NetworkError
)

try:
    result = sdk.cuf(company_name="TechCorp", country_code="US")
except ValidationError as e:
    print(f"Validation error: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after: {e.retry_after} seconds")
except CreditLimitError as e:
    print(f"Credit limit exceeded: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except CufinderError as e:
    print(f"API error: {e}")
```

## Advanced Usage

### Direct Client Access

For advanced usage, you can access the underlying HTTP client:

```python
client = sdk.get_client()

# Make custom requests
response = client.get("/custom-endpoint", params={"param": "value"})
```

### Custom Headers

```python
response = client.post(
    "/endpoint",
    data={"key": "value"},
    headers={"Custom-Header": "value"}
)
```

## Response Models

All responses are strongly typed using Pydantic models:

```python
from cufinder.models import CufResponse, EppResponse, LbsResponse

# CUF Response
domain: CufResponse = sdk.cuf("TechCorp", "US")
print(domain.domain)
print(domain.confidence)

# EPP Response  
profile: EppResponse = sdk.epp("https://linkedin.com/in/johndoe")
print(profile.person.full_name)
print(profile.company.name)

# LBS Response
businesses: LbsResponse = sdk.lbs(city="San Francisco")
print(businesses.total)
print(businesses.businesses[0]["name"])
```

## Development

### Setup

```bash
git clone https://github.com/CUFinder/cufinder-py.git
cd cufinder-py
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@cufinder.io
- 📖 Documentation: [https://docs.cufinder.io/python](https://docs.cufinder.io/python)
- 🐛 Issues: [https://github.com/CUFinder/cufinder-py/issues](https://github.com/CUFinder/cufinder-py/issues)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

# vaultik-api-client

Official Python client for Vaultik AI Authentication API.

## Installation

```bash
pip install vaultik-api-client
```

## Quick Start

```python
from vaultik import VaultikClient

client = VaultikClient(api_key='vaultik_...')

# Analyze product
result = client.analyze(
    image_paths=['watch1.jpg', 'watch2.jpg'],
    metadata={
        'productBrand': 'Rolex',
        'productName': 'Submariner'
    }
)

print(f"Certificate ID: {result['certificateId']}")
```

## Features

- ✅ Type hints throughout
- ✅ Async support
- ✅ Automatic polling
- ✅ Photo challenge handling
- ✅ Progress callbacks
- ✅ Comprehensive error handling
- ✅ Python 3.8+

## Documentation

Full documentation: https://app.vaultik.com/dashboard/developer/docs

## License

MIT

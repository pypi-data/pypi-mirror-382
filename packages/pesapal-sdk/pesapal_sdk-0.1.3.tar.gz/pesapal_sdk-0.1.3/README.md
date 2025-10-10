# Pesapal Python SDK

Unofficial Python SDK for [Pesapal API 3.0](https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json/api-reference)

## Features

-   Automatic token management and refresh
-   Type-safe request models
-   Clean, intuitive API
-   Comprehensive docs
-   Good test coverage

## Installation

```
pip install pesapal-sdk
```

## Quickstart

```python
from pesapal_sdk import PesapalClient
from pesapal_sdk.models import OrderRequest, BillingAddress
from decimal import Decimal

# Initialize client
client = PesapalClient(
    consumer_key="<YOUR-PESAPAL-CONSUMER-KEY>",
    consumer_secret="<YOUR-PESAPAL-CONSUMER-SECRET>",
    environment="sandbox" # or "production"
)

# Register IPN URL (one-time setup)
ipn_response = client.ipn.register("https://yoursite.com/ipn")
ipn_id = ipn_response["ipn_id"]

# Create billing address
billing = BillingAddress(
    email_address="customer@example.com",
    phone_number="0712345678",
    country_code="KE",
    first_name="Kevin",
    last_name="Kimani",
    line1="Juja, Kenya"
)

# Submit order
order = OrderRequest(
    id="order-123",
    currency="KES",
    amount=Decimal("1000.00"),
    description="Payment for services",
    callback_url="https://yoursite.com/callback",
    notification_id=ipn_id,
    billing_address=billing
)

response = client.transactions.submit_order(order)
print(f"Redirect URL: {response['redirect_url']}")

# Check transaction status
status = client.transactions.get_status(response["order_tracking_id"])
print(f"Status: {status['payment_status_description']}")
```

## Requirements

-   Python 3.8+
-   requests

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE.md) file for details.

## Support

-   Documentation: [Pesapal API Docs](https://developer.pesapal.com/how-to-integrate/e-commerce/api-30-json/api-reference)
-   Issues: [GitHub Issues](https://github.com/kimanikevin254/pesapal-python-sdk/issues)

## Disclaimer

This is an unofficial SDK and is not affiliated with or endorsed by Pesapal.

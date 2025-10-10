from .auth import TokenManager
from .resources import (
    IPN, Transactions
)
from constants import (
    BASE_PRODUCTION_URL, BASE_SANDBOX_URL
)

class PesapalClient:
    """Main Pesapal SDK client"""

    def __init__(self, consumer_key: str, consumer_secret: str, environment: str = "sandbox"):
        """
        Initialize Pesapal client
        
        Args:
            consumer_key: Your Pesapal consumer key
            consumer_secret: Your Pesapal consumer secret
            environment: Your integration environment (either 'sandbox' or 'production')
        """
        base_urls = {
            'sandbox': BASE_SANDBOX_URL,
            'production': BASE_PRODUCTION_URL
        }

        self.base_url = base_urls.get(environment)
        if not self.base_url:
            raise ValueError(f"Invalid Pesapal environment: {environment}")
        
        self.token_manager = TokenManager(base_url=self.base_url, consumer_key=consumer_key, consumer_secret=consumer_secret)
        self.ipn = IPN(token_manager=self.token_manager, base_url=self.base_url)
        self.transactions = Transactions(token_manager=self.token_manager, base_url=self.base_url)

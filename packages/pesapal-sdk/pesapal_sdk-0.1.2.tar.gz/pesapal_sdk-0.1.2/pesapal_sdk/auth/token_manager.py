import threading
import requests
from typing import Optional
from datetime import datetime, timedelta, timezone

from pesapal_sdk.constants import AUTHENTICATION_ENDPOINT, DEFAULT_TIMEOUT_SECS 

class TokenManager:
    """Handle token generation, caching, and refresh"""
    
    def __init__(self, base_url: str, consumer_key: str, consumer_secret: str):
        self.base_url = base_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        self.token_endpoint = f"{self.base_url}{AUTHENTICATION_ENDPOINT}"

        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._lock = threading.Lock()

        # Refresh token 30secs before expiry to avoid edge cases
        self._refresh_buffer_secs = 30

    def get_token(self) -> str:
        """Retrieve valid token"""
        with self._lock:
            if self._is_token_valid():
                return self._token
            return self._refresh_token()

    def _is_token_valid(self) -> bool:
        """Check if current token is valid"""
        if not self._token or not self._token_expiry:
            return False
        return datetime.now(timezone.utc) + timedelta(seconds=self._refresh_buffer_secs) < self._token_expiry
    
    def _refresh_token(self) -> str:
        """Request a new token from Pesapal"""
        payload = {
            'consumer_key': self.consumer_key,
            'consumer_secret': self.consumer_secret
        }

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                url=self.token_endpoint,
                headers=headers,
                json=payload,
                timeout=DEFAULT_TIMEOUT_SECS
            )
            response.raise_for_status()

            data = response.json()

            self._token = data.get('token')

            if not self._token:
                raise ValueError('No token received from Pesapal')
            
            # Pesapal tokens are valid for 5 minutes (300 seconds)
            # Set expiry to 4.5 minutes to be safe
            self._token_expiry = datetime.now(timezone.utc) + timedelta(seconds=270)

            return self._token
        
        except requests.RequestException as e:
            raise Exception(f'Failed to authenticate with Pesapal: {str(e)}')
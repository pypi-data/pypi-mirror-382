import requests
from typing import Dict, Optional, Any

from pesapal_sdk.auth.token_manager import TokenManager
from pesapal_sdk.constants import DEFAULT_TIMEOUT_SECS

class BaseResource:
    """Base class for all API resource classes"""
    def __init__(self, token_manager: TokenManager, base_url: str):
        self.token_manager = token_manager
        self.base_url = base_url

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[Any, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ):
        """Make authenticated request to Pesapal API"""
        token = self.token_manager.get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method, url=url, headers=headers,
                json=json, params=params, timeout=DEFAULT_TIMEOUT_SECS
            )

            response.raise_for_status()

            return response.json()
        
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                # Retry with fresh token
                token = self.token_manager.get_token()
                headers['Authorization'] = f'Bearer {token}'

                response = requests.request(
                    method, url, headers=headers,
                    json=json, params=params, timeout=DEFAULT_TIMEOUT_SECS
                )

                response.raise_for_status()

                return response.json()
            
            raise Exception(e.response.status_code, e.response.text)
        
        except requests.RequestException as e:
            raise Exception(str(e))
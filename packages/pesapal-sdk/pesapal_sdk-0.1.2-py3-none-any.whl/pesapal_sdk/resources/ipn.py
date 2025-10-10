from .base import BaseResource
from pesapal_sdk.constants import IPN_REGISTRATION_ENDPOINT, IPN_LIST_ENDPOINT

class IPN(BaseResource):
    """Handle IPN (Instant Payment Notification) operations"""
    
    def register(self, url: str, ipn_notification_type: str = 'GET'):
        """
        Register IPN URL for payment notifications
        
        Args:
            url: The notification url Pesapal with send a status alert to
            ipn_notification_type: GET or POST. This is the http request method Pesapal will use when triggering the IPN alert (default: GET)
        
        Returns:
            Dict with ipn_id and other details
        """
        payload = {
            'url': url,
            'ipn_notification_type': ipn_notification_type
        }

        return self._make_request(
            method='POST',
            endpoint=IPN_REGISTRATION_ENDPOINT,
            json=payload
        )
    
    def list(self):
        """
        Fetch all registered IPN URLs for a particular Pesapal merchant account
        
        Args:
            None

        Returns:
            A list of all registered IPN URLs for a merchant account
        """
        return self._make_request(
            method='GET',
            endpoint=IPN_LIST_ENDPOINT
        )
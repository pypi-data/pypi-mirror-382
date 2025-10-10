from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Optional
from datetime import date
from enum import Enum

@dataclass(kw_only=True)
class BillingAddress:
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    country_code: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[int] = None
    zip_code: Optional[int] = None

    def __post_init__(self):
        """Validate fields after initialization"""
        if not self.phone_number and not self.email_address:
            raise ValueError(
                f"Both phone_number and email_address cannot be empty. "
                f"You must provide a value for either of them"
            )
        
        if self.country_code and len(self.country_code) != 2:
            raise ValueError(
                f"Country code should be 2 characters long"
                f"and in ISO 3166-1 format"
            )
    
    def to_dict(self):
        return asdict(self)


@dataclass(kw_only=True)
class OrderRequest:
    id: str
    currency: str
    amount: Decimal
    description: str
    callback_url: str
    notification_id: str
    billing_address: BillingAddress
    redirect_mode: Optional[str] = None
    cancellation_url: Optional[str] = None
    branch: Optional[str] = None

    def __post_init__(self):
        """Validate fields after initialization"""
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter code (e.g., KES)")
        
        if not self.callback_url.startswith(('http://', 'https://')):
            raise ValueError("callback_url must be a valid URL")
        
    def to_dict(self):
        data = asdict(self)
        # Convert Decimal to float for JSON serialization
        data['amount'] = float(data['amount'])
        return data

class Frequency(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

@dataclass(kw_only=True)
class SubscriptionDetails:
    start_date: date
    end_date: date
    frequency: Frequency

    def __post_init__(self):
        # Check if provided frequncy value is valid
        if not isinstance(self.frequency, Frequency):
            try:
                self.frequency = Frequency(self.frequency)
            except ValueError:
                raise ValueError(
                    f"Invalid subscription frequency '{self.frequency}'. "
                    f"Must be one of: {[f.value for f in Frequency]}"
                )

    def to_dict(self):
        return asdict(self)

@dataclass(kw_only=True)
class SubscriptionPayment(OrderRequest): # Inherits OrderRequest because it requires all the attrs in the class and few others
    account_number: str # Customer identification number known to your system
    subscription_details: Optional[SubscriptionDetails] = None

    def to_dict(self):
        return asdict(self)
    

@dataclass(kw_only=True)
class RefundRequest:
    confirmation_code: str
    amount: Decimal
    username: str
    remarks: str

    def to_dict(self):
        data = asdict(self)
        # Convert decimal to float for serialization
        data['amount'] = float(data['amount'])
        return data
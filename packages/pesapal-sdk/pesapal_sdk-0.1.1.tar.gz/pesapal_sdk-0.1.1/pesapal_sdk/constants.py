BASE_SANDBOX_URL = "https://cybqa.pesapal.com/pesapalv3/api"
BASE_PRODUCTION_URL = "https://pay.pesapal.com/v3/api"

DEFAULT_TIMEOUT_SECS = 30

AUTHENTICATION_ENDPOINT = "/Auth/RequestToken"
IPN_REGISTRATION_ENDPOINT = "/URLSetup/RegisterIPN"
IPN_LIST_ENDPOINT = "/URLSetup/GetIpnList"
SUBMIT_ORDER_REQUEST_ENDPOINT = "/Transactions/SubmitOrderRequest"
TRANSACTION_STATUS_ENDPOINT = "/Transactions/GetTransactionStatus"
REFUND_REQUEST_ENDPOINT = "/Transactions/RefundRequest"
ORDER_CANCELLATION_ENDPOINT = "/Transactions/CancelOrder"
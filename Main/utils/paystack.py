import requests
from django.conf import settings

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_BASE_URL = "https://api.paystack.co"

def verify_paystack_payment(reference):
    """Verify a Paystack payment transaction."""
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}

    response = requests.get(url, headers=headers)
    response_data = response.json()

    if response_data["status"]:
        return response_data["data"]  # Returns transaction details
    return None

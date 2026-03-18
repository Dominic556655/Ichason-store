import requests
from django.conf import settings

def get_usd_to_ngn_rate():
    url = f"https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_API_KEY}/latest/USD"
    
    try:
        response = requests.get(url)
        data = response.json()

        if data["result"] == "success":
            return data["conversion_rates"]["NGN"]

    except Exception as e:
        print("Exchange rate error:", e)

    return None
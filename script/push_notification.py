import os
import requests
import logging
import json

logger = logging.getLogger(__name__)

'''
    Message shape
    {
        "battery": 91,
        "battery_low": false,
        "linkquality": 255,
        "water_leak": false
    }
'''
def send_notification(
    topic: str,
    payload_str: str
):
    api_url = 'https://api.pushover.net/1/messages.json'
    token = os.getenv('PUSHOVER_APP')
    user = os.getenv('PUSHOVER_USER')    

    # Check pushover api tokens are set
    if not token or not user:
        raise ValueError("Error: Missing environment settings")
    # Check data format
    if not payload_str or not isinstance(payload_str, str):
        raise ValueError("Message type is not correct")

    # Convert to dict
    data = json.loads(payload_str)
    leak = data.get('water_leak')
    battery_low = data.get('battery_low')

    notification = f'Sensor {topic} | Leak detected {leak} | Low battery {battery_low}'

    payload = {
        "token": token,
        "user": user,
        "message": notification,
    }

    if leak or battery_low:
        try:
            # Response from Pushover API
            response = requests.post(api_url, data=payload)
            response.raise_for_status()
            logger.info(f"Response result: {response.json()}")
        except requests.RequestException as e:
            logger.error(f"Pushover API Error: {e} \nResponse: {getattr(e.response, 'text', '')}")
            raise
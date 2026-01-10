import os
import requests
import logging

logger = logging.getLogger(__name__)

def send_notification(
    message: str,
):
    api_url = 'https://api.pushover.net/1/messages.json'
    token = os.getenv('PUSHOVER_APP')
    user = os.getenv('PUSHOVER_USER')
    
    if not token or not user:
        raise ValueError("Error: Missing environment settings")

    if not message or not isinstance(message, str):
        raise ValueError("Message must be a non-empty string")

    payload = {
        "token": token,
        "user": user,
        "message": message,
    }

    try:
        # Response from Pushover API
        response = requests.post(api_url, data=payload)
        response.raise_for_status()
        print('Response result: ', response.json())
    except requests.RequestException as e:
        logger.error(f"Pushover API Error: {e} \nResponse: {getattr(e.response, 'text', '')}")
        raise
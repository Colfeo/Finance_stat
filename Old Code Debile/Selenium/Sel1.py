import requests
import json
import hashlib
import hmac
from time import time

# Replace these values with your actual Binance API key and secret key
API_KEY = 'XGYQzrx0lt7SOHLuXsVtvP9fq6VZ14kS4k5vJKuNiP6nuicytVJa3aWyGkfRhG4u'
SECRET_KEY = 'V0UY8RUSoHcRWxc0JXSRjF7s9gGpoqMGM317LyNkiScpeGIr3pjZrDeAzaIB5DqE'

# URL for the Binance API endpoint to get the futures leaderboard
ENDPOINT = '/bapi/futures/v2/private/future/leaderboard/getOtherPosition'

# Base URL for the Binance API
BASE_URL = 'https://www.binance.com'

def generate_signature(data):
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()

def binance_authenticated_request(endpoint, params=None):
    try:
        # Generate timestamp (milliseconds since epoch)
        timestamp = int(time() * 1000)

        # Create request parameters
        params = params or {}
        params['timestamp'] = timestamp

        # Generate signature
        signature = generate_signature('&'.join([f'{k}={v}' for k, v in params.items()]))

        # Create request headers
        headers = {
            'X-MBX-APIKEY': API_KEY
        }

        # Add signature to parameters
        params['signature'] = signature

        # Make the authenticated request
        response = requests.get(BASE_URL + endpoint, headers=headers, params=params)

        # Check if request was successful
        response.raise_for_status()

        # Return JSON response
        return response.json()

    except requests.exceptions.RequestException as e:
        # Handle exceptions
        print("Error:", e)
        return None

# Example usage: Get futures leaderboard for a specific encrypted UUID
encrypted_uuid = 'AB82D5988CF0DA3336FA872AE6F99B40'  # Replace with the encrypted UUID
leaderboard_params = {
    "encryptedUid": encrypted_uuid
}

leaderboard_data = binance_authenticated_request(ENDPOINT, params=leaderboard_params)
if leaderboard_data:
    print("Futures Leaderboard for Encrypted UUID", encrypted_uuid)
    print(json.dumps(leaderboard_data, indent=4))

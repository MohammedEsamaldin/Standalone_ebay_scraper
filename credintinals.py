import requests
import base64
import json
from datetime import datetime, timedelta

def fetch_and_store_application_token(client_id, client_secret, filename='ebay_token.json'):
    url = 'https://api.ebay.com/identity/v1/oauth2/token'
    
    credentials = f'{client_id}:{client_secret}'
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_credentials}'
    }
    
    body = {
        'grant_type': 'client_credentials',
        'scope': 'https://api.ebay.com/oauth/api_scope'  # Update this as needed
    }
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    
    data = response.json()
    access_token = data['access_token']
    expires_in = data['expires_in']  # Time in seconds
    
    # Calculate expiry time
    expiry_time = datetime.now() + timedelta(seconds=expires_in)

    # Save the token and expiry time to a file
    with open(filename, 'w') as file:
        json.dump({
            'access_token': access_token,
            'expiry_time': expiry_time.isoformat()
        }, file)

    return access_token



def get_valid_application_token(client_id, client_secret, filename='ebay_token.json'):
    try:
        # Load the current token data
        with open(filename, 'r') as file:
            token_data = json.load(file)
            access_token = token_data['access_token']
            expiry_time = datetime.fromisoformat(token_data['expiry_time'])
        
        # Check if the token is expired
        if datetime.now() >= expiry_time:
            print("Token expired. Fetching a new one.")
            access_token = fetch_and_store_application_token(client_id, client_secret, filename)
        else:
            print("Token is valid.")
        
        return access_token

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # If file not found or invalid file, fetch a new token
        print("Token file not found or invalid. Fetching a new one.")
        return fetch_and_store_application_token(client_id, client_secret, filename)

import requests
import base64
import json
from datetime import datetime, timedelta

def fetch_and_store_application_token(client_id, client_secret, user, filename='ebay_tokens.json'):
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
    expiry_time = datetime.now() + timedelta(seconds=expires_in)
    
    # Load existing tokens
    tokens = load_tokens(filename)
    
    # Update token for the user
    tokens[str(user)] = {
        'access_token': access_token,
        'expiry_time': expiry_time.isoformat()
    }

    # Save the updated tokens
    save_tokens(filename, tokens)

    return access_token

def load_tokens(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_tokens(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def get_valid_application_token(client_id, client_secret, user, filename='ebay_tokens.json'):
    tokens = load_tokens(filename)
    user_str = str(user)
    
    if user_str in tokens:
        token_data = tokens[user_str]
        access_token = token_data['access_token']
        expiry_time = datetime.fromisoformat(token_data['expiry_time'])
        
        if datetime.now() < expiry_time:
            print("Token is valid.")
            return access_token
        else:
            print("Token expired. Fetching a new one.")

    # Fetch a new token if not found or expired
    return fetch_and_store_application_token(client_id, client_secret, user, filename)

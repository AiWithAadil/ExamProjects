import requests
import boto3
import json
import base64
from urllib.parse import urlencode

# Spotify API credentials
CLIENT_ID = "****************"
CLIENT_SECRET = "****************"
REDIRECT_URI = 'https://open.spotify.com/callback/'  # Make sure to register this in your Spotify Developer Dashboard

# AWS Region for CloudWatch
AWS_REGION = 'us-east-1'  # Change to your AWS region

# CloudWatch Event source and detail-type
EVENT_SOURCE = 'custom.spotify'
EVENT_DETAIL_TYPE = 'Spotify API Trigger'

# Step 1: Generate the authorization URL
def get_authorization_url():
    # Use scope for accessing public playlists and tracks
    scope = "playlist-read-private"  # Access public playlists
    auth_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={scope}"
    return auth_url

# Step 2: Exchange authorization code for access token
def get_spotify_token(auth_code):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode("utf-8"),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,  # Authorization code from the previous step
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(url, headers=headers, data=payload)
    response_data = response.json()

    # Check for token in the response
    if 'access_token' in response_data:
        return response_data['access_token']
    else:
        print("Error:", response_data)
        return None

# Step 3: Fetch data from Spotify API (e.g., get public playlists)
def fetch_spotify_data():
    # Replace with the actual authorization code from the URL
    auth_code = 'AQBq8TAkMusnNqSjua3SJrdJQh8k3hDZIxjXmRqVOLR9eE_DBKsVDbiKxV4NEdpigwzasSHg0vSAR5IXu2rcPe-Ksjrn4AjOuCBeraFqtCIdUkB0-lGgH4pIDR-w3hCGYb26rfl3jrXZHGwCpOOdvcCCS6G4QjoRBRexJsfgzOMGRP8bLlht0W4AoI8vv3RrTKxhU12fa-353vAHIw'  # Replace with the actual code after user authorization
    access_token = get_spotify_token(auth_code)

    if access_token is None:
        print("Failed to obtain access token")
        return {}

    url = "https://api.spotify.com/v1/me/playlists"  # Example endpoint for public data (replace as needed)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Function to send custom event to CloudWatch
def send_event_to_cloudwatch(data):
    # Initialize CloudWatch client
    client = boto3.client('events', region_name=AWS_REGION)

    # Send custom event to CloudWatch
    response = client.put_events(
        Entries=[{
            'Source': EVENT_SOURCE,
            'DetailType': EVENT_DETAIL_TYPE,
            'Detail': json.dumps(data),
            'EventBusName': 'default',  # Use 'default' unless you have a custom event bus
        }]
    )
    print(f"Event sent to CloudWatch: {response}")

# Main function
def main():
    # Step 1: Get the authorization URL
    auth_url = get_authorization_url()
    print(f"Visit this URL and authorize the app: {auth_url}")
    
    # Once you get the authorization code from the URL, replace 'authorization_code_value'
    # with the actual authorization code in your code
    spotify_data = fetch_spotify_data()
    print("Spotify Data:", spotify_data)

    # Send Spotify data to CloudWatch as a custom event
    send_event_to_cloudwatch(spotify_data)

if __name__ == "__main__":
    main()

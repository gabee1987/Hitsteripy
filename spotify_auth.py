import os
import requests
from dotenv import load_dotenv
from logger import log_info, log_error

# Load environment variables from spotify.env
env_file = "spotify.env"
if not os.path.exists(env_file):
    log_error(f"Environment file {env_file} not found.")
    exit(1)

load_dotenv(env_file)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    log_error("Environment variables SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are not set in spotify.env.")
    exit(1)


def get_spotify_token():
    """Authenticate with Spotify API and fetch an access token."""
    try:
        log_info("Fetching Spotify access token...")
        auth_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic ZGZmNmFkNTQ4MmEwNDRiNWI3YTM4NjNiODkzNTQ5NjM6OTZlZWIzYjUwOWM4NDcxNmJlZjVjZjUxMDVmODlkM2Y=",  # Replace this later with a correct encoder
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        response = requests.post(auth_url, headers=headers, data=data)
        response.raise_for_status()
        token = response.json().get("access_token")
        log_info("Spotify access token fetched successfully.")
        return token
    except requests.RequestException as e:
        log_error(f"Failed to fetch Spotify access token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            log_error(f"Response Status Code: {e.response.status_code}")
            log_error(f"Response Content: {e.response.text}")
        raise

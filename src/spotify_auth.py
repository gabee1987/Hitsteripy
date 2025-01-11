import requests
from .logger import log_info, log_error

def get_spotify_token(app_state):
    """Authenticate with Spotify API and fetch an access token using a hardcoded Authorization header."""
    try:
        log_info(app_state, "Fetching Spotify access token...")
        auth_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic ZGZmNmFkNTQ4MmEwNDRiNWI3YTM4NjNiODkzNTQ5NjM6OTZlZWIzYjUwOWM4NDcxNmJlZjVjZjUxMDVmODlkM2Y=",  # Replace this later with a correct encoder
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        response = requests.post(auth_url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        token = response.json().get("access_token")
        log_info(app_state, "Spotify access token fetched successfully.")
        return token
    except requests.RequestException as e:
        log_error(app_state, f"Failed to fetch Spotify access token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            log_error(app_state, f"Response Status Code: {e.response.status_code}")
            log_error(app_state, f"Response Content: {e.response.text}")
        raise

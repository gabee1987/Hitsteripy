import os
import requests
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# Load environment variables
ENV_FILE = "spotify.env"
if not os.path.exists(ENV_FILE):
    print("[ERROR] Environment file spotify.env not found.")
    exit(1)

load_dotenv(ENV_FILE)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Predefined working encoded string (fallback for the manual curl command encoded credentials)
WORKING_ENCODED_CREDENTIALS = "ZGZmNmFkNTQ4MmEwNDRiNWI3YTM4NjNiODkzNTQ5NjM6OTZlZWIzYjUwOWM4NDcxNmJlZjVjZjUxMDVmODlkM2Y="


def validate_credentials():
    """Validate that credentials are properly loaded."""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("[ERROR] Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET.")
        return False
    print("[INFO] Spotify credentials loaded successfully.")
    return True


def clear_cache():
    """Clear Spotipy's .cache file if it exists."""
    cache_file = ".cache"
    if os.path.exists(cache_file):
        print("[INFO] Clearing Spotipy cache...")
        os.remove(cache_file)
        print("[INFO] Spotipy cache cleared.")


def test_spotify_with_spotipy():
    """Test Spotify communication using Spotipy."""
    try:
        print("[INFO] Testing Spotify communication using Spotipy...")
        clear_cache()  # Ensure no invalid tokens are cached
        sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))
        result = sp.search(q="test", type="track", limit=1)
        print("[SUCCESS] Spotipy communication successful.")
        print("[DATA] Example track:", result['tracks']['items'][0]['name'])
    except Exception as e:
        print("[ERROR] Spotipy test failed:", str(e))


def test_spotify_with_authorization_header():
    """Test Spotify token fetch with Authorization header."""
    try:
        print("[INFO] Testing Spotify with Authorization header...")
        auth_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {WORKING_ENCODED_CREDENTIALS}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        response = requests.post(auth_url, headers=headers, data=data)
        print("[DEBUG] Response Status:", response.status_code)
        print("[DEBUG] Response Content:", response.text)
        response.raise_for_status()
        token = response.json().get("access_token")
        print("[SUCCESS] Token fetched successfully using Authorization header.")
        print("[DATA] Token:", token[:20], "... (truncated)")
    except requests.RequestException as e:
        print("[ERROR] Authorization header test failed:", e)


def test_spotify_with_query_params():
    """Test Spotify token fetch using query parameters."""
    try:
        print("[INFO] Testing Spotify with query parameters...")
        auth_url = "https://accounts.spotify.com/api/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET
        }
        response = requests.post(auth_url, data=params)
        print("[DEBUG] Response Status:", response.status_code)
        print("[DEBUG] Response Content:", response.text)
        response.raise_for_status()
        token = response.json().get("access_token")
        print("[SUCCESS] Token fetched successfully using query parameters.")
        print("[DATA] Token:", token[:20], "... (truncated)")
    except requests.RequestException as e:
        print("[ERROR] Query parameters test failed:", e)


def fetch_token_and_test_api():
    """Fetch token and use it to test Spotify API."""
    try:
        print("[INFO] Fetching token and testing Spotify API...")
        auth_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {WORKING_ENCODED_CREDENTIALS}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        response = requests.post(auth_url, headers=headers, data=data)
        response.raise_for_status()
        token = response.json().get("access_token")

        # Use token to fetch a track
        api_url = "https://api.spotify.com/v1/tracks/6rqhFgbbKwnb9MLmUQDhG6"
        headers = {"Authorization": f"Bearer {token}"}
        api_response = requests.get(api_url, headers=headers)
        api_response.raise_for_status()
        print("[SUCCESS] Spotify API test successful.")
        print("[DATA] Track Name:", api_response.json()["name"])
    except requests.RequestException as e:
        print("[ERROR] Spotify API test failed:", e)


if __name__ == "__main__":
    print("[INFO] Starting Spotify communication tests...")
    if not validate_credentials():
        exit(1)

    print("\n[TEST 1] Spotipy Communication:")
    test_spotify_with_spotipy()

    print("\n[TEST 2] Authorization Header:")
    test_spotify_with_authorization_header()

    print("\n[TEST 3] Query Parameters:")
    test_spotify_with_query_params()

    print("\n[TEST 4] Fetch Token and Use API:")
    fetch_token_and_test_api()

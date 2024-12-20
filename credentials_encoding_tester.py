import os
import requests
import subprocess
import base64
from dotenv import load_dotenv

# Load environment variables
env_file = "spotify.env"
if not os.path.exists(env_file):
    print("[ERROR] Environment file spotify.env not found.")
    exit(1)

load_dotenv(env_file)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID").strip()
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET").strip()

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("[ERROR] Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in spotify.env.")
    exit(1)

def encode_credentials(client_id, client_secret):
    """Encode client credentials in Base64."""
    credentials = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    print("[DEBUG] Raw credentials:", credentials)
    print("[DEBUG] Encoded credentials:", encoded)
    return encoded

def compare_encoded_with_curl(encoded):
    """Compare Python-encoded string with the cURL-encoded one."""
    curl_encoded = "ZGZmNmFkNTQ4MmEwNDRiNWI3YTM4NjNiODkzNTQ5NjM6OTZlZWIzYjUwOWM4NDcxNmJlZjVjZjUxMDVmODlkM2Y="
    print("[DEBUG] Python-encoded credentials:", encoded)
    print("[DEBUG] cURL-encoded credentials:", curl_encoded)
    if encoded == curl_encoded:
        print("[SUCCESS] Python-encoded credentials match the cURL-encoded credentials.")
    else:
        print("[ERROR] Python-encoded credentials DO NOT match the cURL-encoded credentials.")

# Tests as before...

if __name__ == "__main__":
    print("[INFO] Starting Spotify communication tests...")
    encoded_credentials = encode_credentials(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    compare_encoded_with_curl(encoded_credentials)

    # Run the other tests...

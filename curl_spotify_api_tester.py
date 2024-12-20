import os
import requests
import subprocess
import base64
from dotenv import load_dotenv

# Load environment variables from spotify.env file
env_file = "spotify.env"
if not os.path.exists(env_file):
    print("[ERROR] Environment file spotify.env not found.")
    exit(1)

load_dotenv(env_file)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

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
    """Compare Python-encoded string with the one used in the working cURL."""
    curl_encoded = "ZGZmNmFkNTQ4MmEwNDRiNWI3YTM4NjNiODkzNTQ5NjM6OTZlZWIzYjUwOWM4NDcxNmJlZjVjZjUxMDVmODlkM2Y="
    print("[DEBUG] Python-encoded credentials:", encoded)
    print("[DEBUG] cURL-encoded credentials:", curl_encoded)
    if encoded == curl_encoded:
        print("[SUCCESS] Python-encoded credentials match the cURL-encoded credentials.")
    else:
        print("[ERROR] Python-encoded credentials DO NOT match the cURL-encoded credentials.")

def test_spotify_with_authorization_header(encoded_credentials):
    """Test Spotify token fetch with Authorization header."""
    print("[INFO] Testing Spotify with Authorization header...")
    auth_url = "https://accounts.spotify.com/api/token"
    auth_headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    auth_data = {"grant_type": "client_credentials"}
    print("[DEBUG] Headers:", auth_headers)
    print("[DEBUG] Data:", auth_data)

    try:
        response = requests.post(auth_url, headers=auth_headers, data=auth_data)
        print("[DEBUG] Response Status:", response.status_code)
        print("[DEBUG] Response Content:", response.text)
        response.raise_for_status()
    except requests.RequestException as e:
        print("[ERROR] Authorization header test failed:", e)

def test_spotify_with_curl(encoded_credentials):
    """Test Spotify token fetch using cURL."""
    print("[INFO] Testing Spotify with cURL...")
    cmd = [
        "curl",
        "-X", "POST",
        "-H", f"Authorization: Basic {encoded_credentials}",
        "-d", "grant_type=client_credentials",
        "https://accounts.spotify.com/api/token"
    ]
    print("[DEBUG] cURL Command:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("[DEBUG] cURL Output:", result.stdout.strip())
    print("[DEBUG] cURL Error:", result.stderr.strip())

def test_spotify_api_with_curl_encoded_string():
    """Test Spotify API directly with the exact encoded string from cURL."""
    print("[INFO] Testing Spotify API with exact cURL-encoded string...")
    auth_url = "https://accounts.spotify.com/api/token"
    auth_headers = {
        "Authorization": "Basic ZGZmNmFkNTQ4MmEwNDRiNWI3YTM4NjNiODkzNTQ5NjM6OTZlZWIzYjUwOWM4NDcxNmJlZjVjZjUxMDVmODlkM2Y=",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    auth_data = {"grant_type": "client_credentials"}
    print("[DEBUG] Headers:", auth_headers)
    print("[DEBUG] Data:", auth_data)

    try:
        response = requests.post(auth_url, headers=auth_headers, data=auth_data)
        print("[DEBUG] Response Status:", response.status_code)
        print("[DEBUG] Response Content:", response.text)
        response.raise_for_status()
    except requests.RequestException as e:
        print("[ERROR] Exact cURL-encoded string test failed:", e)

if __name__ == "__main__":
    print("[INFO] Starting Spotify communication tests...")

    # Step 1: Encode credentials and compare with cURL
    encoded_credentials = encode_credentials(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    compare_encoded_with_curl(encoded_credentials)

    # Step 2: Test with Authorization header
    test_spotify_with_authorization_header(encoded_credentials)

    # Step 3: Test with cURL directly
    test_spotify_with_curl(encoded_credentials)

    # Step 4: Test with exact cURL-encoded string
    test_spotify_api_with_curl_encoded_string()

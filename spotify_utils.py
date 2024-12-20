import os
import requests
import base64
from logger import log_info, log_error
import logging

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

print("SPOTIFY_CLIENT_ID:", SPOTIFY_CLIENT_ID)
print("SPOTIFY_CLIENT_SECRET:", SPOTIFY_CLIENT_SECRET)


if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    log_error("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables.")
    exit(1)


def base64_encode(data):
    """Encode a string in Base64 format."""
    return base64.b64encode(data.encode()).decode()


# Enable requests debugging
logging.basicConfig(level=logging.DEBUG)

def get_spotify_token():
    """Retrieve a Spotify API token using Client Credentials Flow."""
    log_info("Fetching Spotify API token...")
    try:
        # Manually encode client_id:client_secret to Base64
        auth = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        encoded_auth = base64.b64encode(auth.encode()).decode()

        # Replicate the curl command's headers and data
        headers = {"Authorization": f"Basic {encoded_auth}"}
        data = {"grant_type": "client_credentials"}

        # Make the POST request
        resp = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

        # Debugging output
        print("Response Status Code:", resp.status_code)
        print("Response Content:", resp.text)

        # Check for successful response
        resp.raise_for_status()
        log_info("Spotify token retrieved successfully.")
        return resp.json()["access_token"]
    except requests.RequestException as e:
        log_error(f"Failed to fetch Spotify API token: {e}")
        if e.response:
            log_error(f"Response Content: {e.response.text}")
        raise




def extract_id_from_url(url):
    """Extract Spotify ID from a track or playlist URL."""
    parts = url.split('/')
    return parts[-1].split('?')[0]


def fetch_track_details(track_id, token):
    """Fetch details for a specific Spotify track."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        log_info(f"Fetching details for track ID: {track_id}")
        r = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers)
        r.raise_for_status()
        data = r.json()
        artist = data['artists'][0]['name']
        song_name = data['name']
        year = data['album']['release_date'].split('-')[0]
        log_info(f"Track details fetched: {artist} - {song_name} ({year})")
        return artist, song_name, year
    except requests.RequestException as e:
        log_error(f"Failed to fetch track details: {e}")
        raise


def fetch_playlist_tracks(playlist_id, token):
    """Fetch all tracks from a Spotify playlist."""
    headers = {"Authorization": f"Bearer {token}"}
    tracks = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    try:
        log_info(f"Fetching tracks for playlist ID: {playlist_id}")
        while url:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()
            for item in data['items']:
                track = item['track']
                if track is None:
                    continue
                artist = track['artists'][0]['name']
                song_name = track['name']
                year = track['album']['release_date'].split('-')[0]
                track_url = track['external_urls']['spotify']
                tracks.append((artist, song_name, year, track_url))
            url = data['next']
        log_info(f"Fetched {len(tracks)} tracks from the playlist.")
        return tracks
    except requests.RequestException as e:
        log_error(f"Failed to fetch playlist tracks: {e}")
        raise

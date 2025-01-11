import sys
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from .spotify_auth import get_spotify_token
from .logger import log_info, log_error

def init_spotify_client(app_state):
    """Initialize a Spotify client and return it."""
    try:
        token = get_spotify_token(app_state)
        sp = Spotify(auth=token)
        log_info(app_state, "Spotify client successfully initialized.")
        return sp
    except Exception as e:
        log_error(app_state, f"Failed to initialize Spotify client: {e}")
        sys.exit(1)

def test_spotify_connection(app_state, sp):
    """Simple test of the Spotify API connection."""
    try:
        log_info(app_state, "Testing Spotify API connection...")
        sp.search(q="test", type="track", limit=1)
        log_info(app_state, "Spotify API connection test successful.")
        return True
    except Exception as e:
        log_error(app_state, f"Spotify connection test failed: {e}")
        return False

def fetch_playlist_name(app_state, sp, playlist_id):
    """Return the actual playlist name from Spotify."""
    playlist = sp.playlist(playlist_id, fields='name')
    name = playlist["name"]
    log_info(app_state, f"Fetched playlist name: {name}")
    return name

def extract_id_from_url(url):
    """Extract the ID portion from a Spotify URL."""
    return url.split("/")[-1].split("?")[0]

def fetch_playlist_tracks(app_state, sp, playlist_url, limit=100):
    """Fetch track data from a Spotify playlist."""
    log_info(app_state, f"Fetching tracks from playlist: {playlist_url}")
    playlist_id = extract_id_from_url(playlist_url)
    results = sp.playlist_items(playlist_id, limit=limit)
    tracks = []

    for item in results.get("items", []):
        track = item.get("track")
        if track:
            tracks.append({
                "artist": track["artists"][0]["name"],
                "song_name": track["name"],
                "year": track["album"]["release_date"].split("-")[0],
                "url": track["external_urls"]["spotify"]
            })
    log_info(app_state, f"Fetched {len(tracks)} tracks from the playlist.")
    return tracks

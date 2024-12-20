import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotify_auth import get_spotify_token
from logger import log_info, log_error

# Initialize Spotipy with client credentials
try:
    log_info("Initializing Spotify client...")
    token = get_spotify_token()
    sp = Spotify(auth=token)
    log_info("Spotify client successfully initialized.")
except Exception as e:
    log_error(f"Failed to initialize Spotify client: {e}")
    exit(1)


def test_spotify_connection():
    """Test connection to Spotify API."""
    try:
        log_info("Testing Spotify API connection...")
        sp.search(q="test", type="track", limit=1)
        log_info("Spotify API connection test successful.")
        return True
    except Exception as e:
        log_error(f"Spotify connection test failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            log_error(f"Response Status Code: {e.response.status_code}")
            log_error(f"Response Content: {e.response.text}")
        return False


def extract_id_from_url(url):
    """Extract Spotify ID from a track or playlist URL."""
    try:
        log_info(f"Extracting Spotify ID from URL: {url}")
        parts = url.split('/')
        spotify_id = parts[-1].split('?')[0]
        log_info(f"Extracted Spotify ID: {spotify_id}")
        return spotify_id
    except Exception as e:
        log_error(f"Failed to extract Spotify ID from URL: {url}")
        log_error(f"Error Details: {e}")
        raise


def fetch_track_details(track_id):
    """Fetch details for a specific Spotify track using Spotipy."""
    try:
        log_info(f"Fetching details for track ID: {track_id}")
        track = sp.track(track_id)
        artist = track['artists'][0]['name']
        song_name = track['name']
        year = track['album']['release_date'].split('-')[0]
        log_info(f"Track details fetched successfully: {artist} - {song_name} ({year})")
        return artist, song_name, year
    except Exception as e:
        log_error(f"Failed to fetch track details for ID: {track_id}")
        log_error(f"Error Details: {e}")
        if hasattr(e, 'response') and e.response is not None:
            log_error(f"Response Status Code: {e.response.status_code}")
            log_error(f"Response Content: {e.response.text}")
        raise


def fetch_playlist_tracks(playlist_id):
    """Fetch all tracks from a Spotify playlist using Spotipy."""
    try:
        log_info(f"Fetching tracks from playlist ID: {playlist_id}")
        results = sp.playlist_items(playlist_id)
        tracks = []
        log_info("Parsing playlist items...")
        for idx, item in enumerate(results['items']):
            track = item.get('track')
            if not track:
                log_error(f"Skipped item at index {idx}: No track data found.")
                continue
            artist = track['artists'][0]['name']
            song_name = track['name']
            year = track['album']['release_date'].split('-')[0]
            track_url = track['external_urls']['spotify']
            tracks.append((artist, song_name, year, track_url))
            log_info(f"Track added: {artist} - {song_name} ({year})")
        log_info(f"Fetched {len(tracks)} tracks from the playlist.")
        return tracks
    except Exception as e:
        log_error(f"Failed to fetch playlist tracks for ID: {playlist_id}")
        log_error(f"Error Details: {e}")
        if hasattr(e, 'response') and e.response is not None:
            log_error(f"Response Status Code: {e.response.status_code}")
            log_error(f"Response Content: {e.response.text}")
        raise

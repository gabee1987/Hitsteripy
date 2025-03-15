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

def fetch_playlist_tracks(app_state, sp, playlist_url, desired_count=100):
    """
    Fetch track data from a Spotify playlist, paginating if necessary.
    desired_count can be an integer or the string 'all'.
    If desired_count > 100, we fetch multiple times in chunks of 100.
    """
    from .logger import log_info, log_error
    from .spotify_utils import extract_id_from_url
    import time

    log_info(app_state, f"Fetching tracks from playlist: {playlist_url}")
    playlist_id = extract_id_from_url(playlist_url)

    # Check if user chose 'all'
    unlimited = (str(desired_count).lower() == 'all')
    if unlimited:
        desired_count = 10_000  # Some large number to ensure we grab all
    else:
        desired_count = int(desired_count)

    all_tracks = []
    offset = 0
    batch_size = 100  # Max Spotify limit per request

    while True:
        try:
            # Calculate how many tracks are still needed
            remaining = desired_count - len(all_tracks)
            if remaining <= 0:
                break  # We already fetched enough

            current_limit = min(batch_size, remaining)  # Ensure we don’t fetch more than needed

            log_info(app_state, f"Batch fetch: offset={offset}, limit={current_limit}")

            results = sp.playlist_items(
                playlist_id,
                limit=current_limit,
                offset=offset
            )

            if "items" not in results:
                log_error(app_state, f"Unexpected API response: {results}")
                break  # Stop if the response is invalid

            items = results.get("items", [])
            if not items:
                break  # No more tracks

            for item in items:
                track = item.get("track")
                if not track:
                    continue
                # Skip the track if it's marked as not playable or missing its Spotify URL.
                if track.get("is_playable") is False or not track.get("external_urls", {}).get("spotify"):
                    continue
                all_tracks.append({
                    "artist": track["artists"][0]["name"],
                    "song_name": track["name"],
                    "year": (track["album"].get("release_date") or "Unknown").split("-")[0],
                    "url": track["external_urls"]["spotify"]
                })


            offset += current_limit

            # **Wait to prevent API rate limiting**
            time.sleep(0.2)  # Wait 200ms before the next request

            # **Stop if there's no more data**
            if results.get("next") is None:
                break

        except Exception as e:
            log_error(app_state, f"Error during fetch: {e}")
            break

    log_info(app_state, f"Fetched {len(all_tracks)} tracks from the playlist.")
    return all_tracks




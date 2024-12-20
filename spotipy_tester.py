import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

playlist_id = "7HGdomqhr1lDRqvqNvffHm"  # Example Playlist
results = sp.playlist_items(playlist_id)
print(results)

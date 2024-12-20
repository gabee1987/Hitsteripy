import os

client_id = os.environ.get("SPOTIFY_CLIENT_ID")
client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

print("SPOTIFY_CLIENT_ID:", os.environ.get("SPOTIFY_CLIENT_ID"))
print("SPOTIFY_CLIENT_SECRET:", os.environ.get("SPOTIFY_CLIENT_SECRET"))

if client_id and client_secret:
    print("Environment variables are set correctly.")
else:
    print("Environment variables are missing or not set.")

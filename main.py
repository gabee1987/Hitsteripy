import os
import shutil
import sys

from spotify_utils import get_spotify_token, extract_id_from_url, fetch_track_details, fetch_playlist_tracks
from card_utils import generate_qr_code, generate_random_gradient, generate_html_and_pdf
from logger import log_info, log_error, log_success


def check_dependencies():
    """Check for required Python modules."""
    required_modules = ["requests", "qrcode", "jinja2", "weasyprint"]
    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        log_error(f"Missing required modules: {', '.join(missing_modules)}")
        log_info("Install missing modules with:")
        log_info("    pip install -r requirements.txt")
        sys.exit(1)


def main():
    try:
        check_dependencies()

        log_info("Paste a Spotify URL (track or playlist) and press Enter:")
        url = input().strip()

        token = get_spotify_token()

        if "track" in url:
            track_id = extract_id_from_url(url)
            artist, song_name, year = fetch_track_details(track_id, token)
            tracks_data = [(artist, song_name, year, url)]
        elif "playlist" in url:
            playlist_id = extract_id_from_url(url)
            tracks_data = fetch_playlist_tracks(playlist_id, token)
        else:
            log_error("URL must be a Spotify track or playlist URL.")
            exit(1)

        if os.path.exists("qrcodes"):
            shutil.rmtree("qrcodes")
        os.makedirs("qrcodes")

        final_tracks = []
        for i, t in enumerate(tracks_data):
            artist, song_name, year, track_url = t
            qr_path = os.path.join("qrcodes", f"track_{i + 1}.png")
            generate_qr_code(track_url, qr_path)
            final_tracks.append({
                "serial_number": f"SN-{i + 1:03}",
                "artist": artist,
                "song_name": song_name,
                "year": year,
                "spotify_url": track_url,
                "qr_code": qr_path
            })

        generate_html_and_pdf(final_tracks)
        log_success("Done! Generated output_front.pdf and output_back.pdf for printing.")

    except Exception as e:
        log_error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()

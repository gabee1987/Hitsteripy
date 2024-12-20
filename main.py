import os
import shutil
from datetime import datetime
from spotify_utils import test_spotify_connection, extract_id_from_url, fetch_track_details, fetch_playlist_tracks
from card_utils import generate_qr_code, generate_html_and_pdf
from logger import log_info, log_error, log_success

def create_output_dir():
    """Create a timestamped output directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("output_pdfs", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def main():
    try:
        # Test connection to Spotify API
        log_info("Checking connection to Spotify API...")
        if not test_spotify_connection():
            log_error("Failed to connect to Spotify API.")
            return
        log_success("Connected to Spotify API successfully.")

        # Get Spotify URL input
        log_info("Paste a Spotify URL (track or playlist) and press Enter:")
        url = input().strip()

        # Determine if URL is for a track or playlist
        if "track" in url:
            log_info("Detected a track URL.")
            track_id = extract_id_from_url(url)
            artist, song_name, year = fetch_track_details(track_id)
            tracks_data = [(artist, song_name, year, url)]
            log_success(f"Track details fetched: {artist} - {song_name} ({year})")
        elif "playlist" in url:
            log_info("Detected a playlist URL.")
            playlist_id = extract_id_from_url(url)
            tracks_data = fetch_playlist_tracks(playlist_id)
            log_success(f"Fetched {len(tracks_data)} tracks from the playlist.")
        else:
            log_error("Invalid URL. Please provide a Spotify track or playlist URL.")
            return

        # Create output directory
        output_dir = create_output_dir()
        log_info(f"Output directory created: {output_dir}")

        # Generate QR codes and prepare data for PDF generation
        for i, t in enumerate(tracks_data):
            artist, song_name, year, track_url = t
            qr_path = os.path.join(output_dir, f"track_{i + 1}.png")
            generate_qr_code(track_url, qr_path)
            tracks_data[i] = {
                "serial_number": f"SN-{i + 1:03}",
                "artist": artist,
                "song_name": song_name,
                "year": year,
                "spotify_url": track_url,
                "qr_code": qr_path
            }

        # Generate HTML and PDF
        generate_html_and_pdf(tracks_data, output_dir)
        log_success(f"Process completed. Files saved in: {output_dir}")
    except Exception as e:
        log_error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

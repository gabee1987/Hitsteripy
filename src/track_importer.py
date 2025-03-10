import os
import csv
from datetime import datetime
from rich.progress import Progress
from .spotify_utils import extract_id_from_url, fetch_playlist_tracks, fetch_playlist_name
from .logger import log_info, log_error, log_success

def import_tracks(app_state, sp, playlist_url, track_count):
    """
    Import tracks from Spotify and save them to a CSV file in imported_tracks/<timestamp>_<track_count>/.
    The CSV file name will use the real playlist name if available.
    """
    log_info(app_state, f"Importing tracks from {playlist_url} with limit={track_count}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("imported_tracks", f"{timestamp}_{track_count}")
    os.makedirs(output_dir, exist_ok=True)

    # Attempt to fetch real playlist name
    playlist_id = extract_id_from_url(playlist_url)
    try:
        real_name = fetch_playlist_name(app_state, sp, playlist_id)
    except Exception:
        real_name = playlist_id  # fallback if fail

    # Sanitize name for filesystem
    safe_name = "".join(c for c in real_name if c.isalnum() or c in [' ', '_', '-']).rstrip()
    csv_filename = f"{safe_name}_tracks.csv"
    output_csv = os.path.join(output_dir, csv_filename)

    # Fetch tracks
    track_data = fetch_playlist_tracks(app_state, sp, playlist_url, desired_count=track_count)

    # Then proceed with writing the CSV, etc.
    with Progress() as progress:
        task = progress.add_task("Importing tracks...", total=len(track_data))
        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Serial Number", "Artist", "Song Name", "Year", "Spotify URL"])
            for i, track in enumerate(track_data):
                writer.writerow([
                    f"SN-{i + 1:03}",
                    track["artist"],
                    track["song_name"],
                    track["year"],
                    track["url"]
                ])
                progress.update(task, advance=1)

    summary = f"{len(track_data)} tracks imported to {output_csv}"
    log_success(app_state, summary)
    return output_csv, summary


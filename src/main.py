import os
import json
from rich.console import Console
from src.logger import log_info, log_error, log_success
from src.spotify_utils import init_spotify_client, test_spotify_connection
from src.track_importer import import_tracks
from src.card_utils import generate_html_cards
from src.menu import create_main_menu, select_playlist, select_track_count

console = Console()

DATA_DIR = "data"
PLAYLIST_HISTORY_FILE = os.path.join(DATA_DIR, "playlist_history.json")
TRACK_COUNT_HISTORY_FILE = os.path.join(DATA_DIR, "track_count_history.json")

def load_history(file_path):
    """Load history data (JSON) from file or return empty list."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(file_path, data):
    """Save JSON data to file with indentation."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def set_playlist_url(app_state):
    """
    Opens a sub-menu to pick a playlist or enter a new URL.
    Stores playlist history as a list of dicts: { "name": "Playlist Name", "url": "..." }
    """
    playlist_history = load_history(PLAYLIST_HISTORY_FILE)

    # The sub-menu returns either None (user cancelled) or a dict {"name": ..., "url": ...}
    chosen_dict = select_playlist(app_state, playlist_history)
    if chosen_dict is None:
        log_info(app_state, "Cancelled playlist selection.")
        return

    # We now have a dictionary with name/url. Let's see if it's new or from history.
    chosen_url = chosen_dict["url"]
    # Save URL and name in app_state
    app_state["playlist_url"] = chosen_url
    app_state["playlist_name"] = chosen_dict["name"]

    # If not already in history, fetch name from Spotify and append
    if not any(p["url"] == chosen_url for p in playlist_history):
        from src.spotify_utils import extract_id_from_url, fetch_playlist_name
        sp = app_state["spotify_client"]
        pid = extract_id_from_url(chosen_url)
        try:
            real_name = fetch_playlist_name(app_state, sp, pid)
        except Exception as e:
            log_error(app_state, f"Failed to fetch playlist name: {e}")
            real_name = "Unknown Playlist"

        new_entry = {"name": real_name, "url": chosen_url}
        playlist_history.insert(0, new_entry)  # Insert at front
        save_history(PLAYLIST_HISTORY_FILE, playlist_history)

        # Update app_state with the real name
        app_state["playlist_name"] = real_name

    # Log both name and URL
    log_success(app_state, f"Playlist set: {app_state['playlist_name']} ({chosen_url})")

def set_track_count(app_state):
    """
    Opens a sub-menu to select or specify the number of tracks to import.
    """
    # Load track count history
    track_count_history = load_history(TRACK_COUNT_HISTORY_FILE)

    # Get the selected track count or None if canceled
    selected_count = select_track_count(app_state, track_count_history)
    if selected_count is None:
        log_info(app_state, "Cancelled track count selection.")
        return

    # Update app_state with the selected track count
    app_state["track_count"] = selected_count

    # Save the selected count to history if it's new
    if selected_count not in track_count_history:
        track_count_history.insert(0, selected_count)
        save_history(TRACK_COUNT_HISTORY_FILE, track_count_history)

    log_success(app_state, f"Track count set to: {selected_count}")

def do_import_tracks(app_state):
    """
    Import tracks from the selected playlist and save them to a CSV file.
    """
    if not app_state["playlist_url"]:
        log_error(app_state, "No playlist URL set. Please set a playlist URL first.")
        return

    if not app_state["track_count"]:
        log_error(app_state, "No track count set. Please set a track count first.")
        return

    sp = app_state["spotify_client"]
    playlist_url = app_state["playlist_url"]
    track_count = app_state["track_count"]

    try:
        csv_file, summary = import_tracks(app_state, sp, playlist_url, track_count)
        app_state["imported_tracks_file"] = csv_file
        log_success(app_state, summary)
    except Exception as e:
        log_error(app_state, f"Failed to import tracks: {e}")

import re
from datetime import datetime

def sanitize_filename(name):
    """
    Remove or replace invalid characters in a file or folder name.
    """
    # Replace invalid characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def do_generate_cards(app_state):
    """
    Generate front/back cards from the imported tracks.
    """
    if not app_state["imported_tracks_file"]:
        log_error(app_state, "No imported tracks found. Please import tracks first.")
        return

    try:
        # Format date and sanitize playlist name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_name = sanitize_filename(app_state["playlist_name"] or "Unknown_Playlist")
        output_dir = os.path.join("generated_cards", f"{timestamp}_{sanitized_name}")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate HTML cards
        summary = generate_html_cards(app_state, app_state["imported_tracks_file"], output_dir)
        log_success(app_state, summary)
    except Exception as e:
        log_error(app_state, f"Failed to generate cards: {e}")


def main():
    app_state = {
        "logs": [],
        "playlist_url": None,
        "playlist_name": None,
        "track_count": None,
        "imported_tracks_file": None,
        "spotify_client": None
    }

    # Init & test Spotify
    sp = init_spotify_client(app_state)
    app_state["spotify_client"] = sp
    if not test_spotify_connection(app_state, sp):
        log_error(app_state, "Spotify connection failed. Exiting...")
        return

    while True:
        result = create_main_menu(app_state)
        if result == "quit":
            console.print("[bold red]Goodbye![/bold red]")
            break

        if result == 0:  # 🎵 Set Playlist URL
            set_playlist_url(app_state)
        elif result == 1:  # 🎼 Set Number of Tracks
            set_track_count(app_state)
        elif result == 2:  # 📂 Import Tracks
            do_import_tracks(app_state)
        elif result == 3:  # 📇 Generate Cards
            do_generate_cards(app_state)
        elif result == 4:  # ❓ Help / Usage
            console.print("[bold cyan]How to Use This App:[/bold cyan]")
            console.print(
                """
[bold green]Steps:[/bold green]
1. Set a Spotify Playlist URL or reuse a previously saved one.
2. Choose the number of tracks to import (or all available tracks).
3. Import tracks, which are saved as CSV files in `imported_tracks/`.
4. Generate printable front/back cards (HTML) in `generated_cards/`.
5. Print the cards.
"""
            )
            console.input("[bold green]Press Enter to return to the main menu.[/bold green]")

if __name__ == "__main__":
    main()

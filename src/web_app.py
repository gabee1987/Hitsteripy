"""
Flask web application for Hitsteripy
Provides a web-based GUI for the Spotify track card generator.
"""
import os
import sys
import json
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.serving import make_server

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from src.logger import log_info, log_error, log_success
from src.spotify_utils import init_spotify_client, test_spotify_connection, extract_id_from_url, fetch_playlist_name
from src.track_importer import import_tracks
from src.card_utils import generate_html_cards
import re

# Setup Flask with correct paths
web_templates_dir = os.path.join(parent_dir, 'web_templates')
web_static_dir = os.path.join(parent_dir, 'web_static')

# Create directories if they don't exist
os.makedirs(web_templates_dir, exist_ok=True)
os.makedirs(web_static_dir, exist_ok=True)

app = Flask(__name__, 
            template_folder=web_templates_dir,
            static_folder=web_static_dir)

# App state (shared across requests)
app_state = {
    "logs": [],
    "playlist_url": None,
    "playlist_name": None,
    "track_count": None,
    "imported_tracks_file": None,
    "spotify_client": None
}

DATA_DIR = "data"
PLAYLIST_HISTORY_FILE = os.path.join(DATA_DIR, "playlist_history.json")
TRACK_COUNT_HISTORY_FILE = os.path.join(DATA_DIR, "track_count_history.json")

def load_history(file_path):
    """Load history data (JSON) from file or return empty list."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(file_path, data):
    """Save JSON data to file with indentation."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def sanitize_filename(name):
    """Remove or replace invalid characters in a file or folder name."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# Initialize Spotify client (will be called before first request)
def init_spotify():
    """Initialize Spotify client when app starts."""
    try:
        sp = init_spotify_client(app_state)
        app_state["spotify_client"] = sp
        if test_spotify_connection(app_state, sp):
            log_info(app_state, "Spotify connection successful")
        else:
            log_error(app_state, "Spotify connection test failed")
    except Exception as e:
        log_error(app_state, f"Failed to initialize Spotify: {e}")

# Initialize Spotify before first request
def ensure_spotify_init():
    """Ensure Spotify is initialized."""
    if app_state.get("spotify_client") is None:
        init_spotify()

# Routes
@app.route('/')
def index():
    """Main page."""
    ensure_spotify_init()
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current app status."""
    ensure_spotify_init()
    return jsonify({
        "playlist_url": app_state.get("playlist_url"),
        "playlist_name": app_state.get("playlist_name"),
        "track_count": app_state.get("track_count"),
        "imported_tracks_file": app_state.get("imported_tracks_file"),
        "logs": app_state.get("logs", [])[-10:],  # Last 10 logs
        "spotify_connected": app_state.get("spotify_client") is not None
    })

@app.route('/api/playlists/history')
def get_playlist_history():
    """Get playlist history."""
    ensure_spotify_init()
    history = load_history(PLAYLIST_HISTORY_FILE)
    return jsonify(history)

@app.route('/api/playlists/set', methods=['POST'])
def set_playlist():
    """Set playlist URL."""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"success": False, "error": "URL is required"}), 400
    
    try:
        playlist_history = load_history(PLAYLIST_HISTORY_FILE)
        playlist_id = extract_id_from_url(url)
        
        # Fetch playlist name
        sp = app_state.get("spotify_client")
        if not sp:
            return jsonify({"success": False, "error": "Spotify not connected"}), 500
        
        playlist_name = fetch_playlist_name(app_state, sp, playlist_id)
        
        # Update app state
        app_state["playlist_url"] = url
        app_state["playlist_name"] = playlist_name
        
        # Save to history if new
        if not any(p["url"] == url for p in playlist_history):
            new_entry = {"name": playlist_name, "url": url}
            playlist_history.insert(0, new_entry)
            save_history(PLAYLIST_HISTORY_FILE, playlist_history)
        
        log_success(app_state, f"Playlist set: {playlist_name} ({url})")
        
        return jsonify({
            "success": True,
            "playlist_name": playlist_name,
            "playlist_url": url
        })
    except Exception as e:
        error_msg = str(e)
        log_error(app_state, f"Failed to set playlist: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), 500

@app.route('/api/tracks/count/history')
def get_track_count_history():
    """Get track count history."""
    history = load_history(TRACK_COUNT_HISTORY_FILE)
    # Default options
    defaults = ["1", "10", "50", "100", "200", "all"]
    return jsonify({"history": history, "defaults": defaults})

@app.route('/api/tracks/count/set', methods=['POST'])
def set_track_count():
    """Set track count."""
    data = request.json
    count = data.get('count', '').strip()
    
    if not count:
        return jsonify({"success": False, "error": "Count is required"}), 400
    
    app_state["track_count"] = count
    
    # Save to history if new
    track_count_history = load_history(TRACK_COUNT_HISTORY_FILE)
    if count not in track_count_history:
        track_count_history.insert(0, count)
        save_history(TRACK_COUNT_HISTORY_FILE, track_count_history)
    
    log_success(app_state, f"Track count set to: {count}")
    
    return jsonify({"success": True, "track_count": count})

@app.route('/api/tracks/import', methods=['POST'])
def import_tracks_endpoint():
    """Import tracks from playlist."""
    if not app_state.get("playlist_url"):
        return jsonify({"success": False, "error": "No playlist URL set"}), 400
    
    if not app_state.get("track_count"):
        return jsonify({"success": False, "error": "No track count set"}), 400
    
    try:
        sp = app_state.get("spotify_client")
        if not sp:
            return jsonify({"success": False, "error": "Spotify not connected"}), 500
        
        playlist_url = app_state["playlist_url"]
        track_count = app_state["track_count"]
        
        csv_file, summary = import_tracks(app_state, sp, playlist_url, track_count)
        app_state["imported_tracks_file"] = csv_file
        
        log_success(app_state, summary)
        
        return jsonify({
            "success": True,
            "csv_file": csv_file,
            "summary": summary
        })
    except Exception as e:
        error_msg = str(e)
        log_error(app_state, f"Failed to import tracks: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), 500

@app.route('/api/cards/csv-files')
def get_csv_files():
    """Get list of imported CSV files."""
    base_dir = "imported_tracks"
    if not os.path.isdir(base_dir):
        return jsonify([])
    
    files = []
    for subdir_name in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir_name)
        if not os.path.isdir(subdir_path):
            continue
        
        for file_name in os.listdir(subdir_path):
            if file_name.lower().endswith(".csv"):
                csv_path = os.path.join(subdir_path, file_name)
                files.append({
                    "label": f"{subdir_name} -> {file_name}",
                    "path": csv_path,
                    "name": file_name
                })
    
    return jsonify(files)

@app.route('/api/cards/generate', methods=['POST'])
def generate_cards_endpoint():
    """Generate cards from CSV."""
    data = request.json
    csv_path = data.get('csv_path')
    
    if not csv_path or not os.path.exists(csv_path):
        return jsonify({"success": False, "error": "CSV file not found"}), 400
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_name = sanitize_filename(app_state.get("playlist_name") or "Unknown_Playlist")
        output_dir = os.path.join("generated_cards", f"{timestamp}_{sanitized_name}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        summary = generate_html_cards(app_state, csv_path, output_dir)
        
        log_success(app_state, summary)
        
        return jsonify({
            "success": True,
            "output_dir": output_dir,
            "summary": summary
        })
    except Exception as e:
        error_msg = str(e)
        log_error(app_state, f"Failed to generate cards: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), 500

@app.route('/api/cards/preview', methods=['POST'])
def preview_card():
    """Generate a preview of a single card."""
    data = request.json
    csv_path = data.get('csv_path')
    track_index = data.get('track_index', 0)
    side = data.get('side', 'front')  # 'front' or 'back'
    
    if not csv_path or not os.path.exists(csv_path):
        return jsonify({"success": False, "error": "CSV file not found"}), 400
    
    try:
        import csv
        from jinja2 import Template
        from src.card_utils import generate_random_gradient, generate_custom_qr_data_uri
        from src.constants import BACKGROUND_IMAGE_FILENAME
        from src.path_utils import get_template_path, get_asset_path
        
        # Read CSV and get the track
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            tracks = list(reader)
        
        if track_index >= len(tracks):
            return jsonify({"success": False, "error": "Track index out of range"}), 400
        
        track = tracks[track_index]
        idx = track_index + 1
        card_num_str = f"#{idx:03d}"
        
        # Prepare track data
        track_data = {
            "artist": track["Artist"],
            "year": track["Year"],
            "song_name": track["Song Name"],
            "gradient": generate_random_gradient(),
            "front_serial": f"Front-{card_num_str}",
            "back_serial": f"Back-{card_num_str}",
            "qr_data_uri": generate_custom_qr_data_uri(
                track["Spotify URL"],
                box_size=4,
                border=2,
                fill_color="black",
                back_color=(255, 255, 255)
            )
        }
        
        # Load template
        if side == 'front':
            template_path = get_template_path("cards_front_template.html")
        else:
            template_path = get_template_path("cards_back_template.html")
        
        with open(template_path, "r", encoding="utf-8") as f:
            template_str = f.read()
        
        # Load CSS
        css_path = get_template_path("cards.css")
        background_image_path = get_asset_path(BACKGROUND_IMAGE_FILENAME)
        
        from src.card_utils import embed_css_with_background
        embedded_css = embed_css_with_background(css_path, background_image_path)
        
        # Render template
        template = Template(template_str)
        html = template.render(
            tracks=[track_data],
            css_embedded=embedded_css,
            page_number=1,
            total_pages=1
        )
        
        return jsonify({
            "success": True,
            "html": html
        })
    except Exception as e:
        error_msg = str(e)
        return jsonify({"success": False, "error": error_msg}), 500

@app.route('/api/logs')
def get_logs():
    """Get application logs."""
    ensure_spotify_init()
    return jsonify(app_state.get("logs", []))

# Serve generated cards
@app.route('/generated_cards/<path:filename>')
def serve_generated_card(filename):
    """Serve generated card HTML files."""
    ensure_spotify_init()
    # Handle nested paths (subdirectories)
    path_parts = filename.split('/')
    if len(path_parts) > 1:
        subdir = '/'.join(path_parts[:-1])
        filename_only = path_parts[-1]
        return send_from_directory(os.path.join('generated_cards', subdir), filename_only)
    return send_from_directory('generated_cards', filename)

def run_web_app(host='127.0.0.1', port=5000, open_browser=True):
    """Run the Flask web application."""
    # Initialize Spotify
    try:
        sp = init_spotify_client(app_state)
        app_state["spotify_client"] = sp
        if not test_spotify_connection(app_state, sp):
            log_error(app_state, "Spotify connection failed")
    except Exception as e:
        log_error(app_state, f"Failed to initialize Spotify: {e}")
    
    # Open browser after a short delay
    if open_browser:
        def open_browser_delayed():
            import time
            time.sleep(1.5)  # Wait for server to start
            url = f"http://{host}:{port}"
            webbrowser.open(url)
        
        browser_thread = threading.Thread(target=open_browser_delayed)
        browser_thread.daemon = True
        browser_thread.start()
    
    print(f"\n{'='*60}")
    print(f"  Hitsteripy Web App is running!")
    print(f"  Open your browser at: http://{host}:{port}")
    print(f"  Press Ctrl+C to stop the server")
    print(f"{'='*60}\n")
    
    app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_web_app()


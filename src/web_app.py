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

# Get base directory for runtime data (where exe is running from, not PyInstaller temp)
def get_base_dir():
    """Get the base directory for runtime data files.
    
    In PyInstaller bundle: Returns the directory where the exe is running from
    In development: Returns the project root directory
    """
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle - use the directory where exe is located
        # sys.executable is the path to the exe file
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # Running in development - use project root
        return str(parent_dir)

base_dir = get_base_dir()

# Initialize data directories relative to base_dir
DATA_DIR = os.path.join(base_dir, "data")
PLAYLIST_HISTORY_FILE = os.path.join(DATA_DIR, "playlist_history.json")
TRACK_COUNT_HISTORY_FILE = os.path.join(DATA_DIR, "track_count_history.json")

# Ensure data directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(base_dir, "generated_cards"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "imported_tracks"), exist_ok=True)

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

# Verify template exists
template_path = os.path.join(web_templates_dir, 'index.html')
if not os.path.exists(template_path):
    print(f"WARNING: Template not found at {template_path}")
else:
    print(f"Template found at: {template_path}")

app = Flask(__name__, 
            template_folder=web_templates_dir,
            static_folder=web_static_dir,
            static_url_path='/static')

# Disable caching in development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# App state (shared across requests)
app_state = {
    "logs": [],
    "playlist_url": None,
    "playlist_name": None,
    "track_count": None,
    "imported_tracks_file": None,
    "spotify_client": None
}

# DATA_DIR will be set after base_dir is defined
# See below for actual initialization

def load_history(file_path):
    """Load history data (JSON) from file or return empty list."""
    # Ensure directory exists
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(file_path, data):
    """Save JSON data to file with indentation."""
    # Ensure directory exists
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
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
    print("=" * 60)
    print("[DEBUG] INDEX ROUTE CALLED!")
    print("=" * 60)
    
    ensure_spotify_init()
    # Add cache-busting for development
    import time
    cache_bust = int(time.time())
    
    # Log template path for debugging
    template_path = os.path.join(web_templates_dir, 'index.html')
    print(f"[DEBUG] Template path: {template_path}")
    print(f"[DEBUG] Template exists: {os.path.exists(template_path)}")
    
    if not os.path.exists(template_path):
        return f"ERROR: Template not found at {template_path}", 500
    
    # Read raw template content to verify
    with open(template_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()
        print(f"[DEBUG] Template file size: {len(raw_content)} bytes")
        print(f"[DEBUG] Template contains 'themeToggle': {'themeToggle' in raw_content}")
        print(f"[DEBUG] Template contains 'Version check: v2': {'Version check: v2' in raw_content}")
    
    # Use Flask's render_template (which has Flask context like url_for)
    # Flask's template caching is already disabled via app.jinja_env.auto_reload = True
    html_content = render_template('index.html', cache_bust=cache_bust)
    
    print(f"[DEBUG] Rendered HTML size: {len(html_content)} bytes")
    print(f"[DEBUG] Rendered HTML contains 'themeToggle': {'themeToggle' in html_content}")
    print(f"[DEBUG] Rendered HTML contains 'Version check: v2': {'Version check: v2' in html_content}")
    print("=" * 60)
    
    # Create response with cache-busting headers
    from flask import Response
    response = Response(html_content, mimetype='text/html')
    # Prevent caching in development
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    return response

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
    ensure_spotify_init()
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
        else:
            # Move to front if already exists
            playlist_history = [p for p in playlist_history if p["url"] != url]
            playlist_history.insert(0, {"name": playlist_name, "url": url})
        
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

@app.route('/api/playlists/delete', methods=['POST'])
def delete_playlist():
    """Delete playlist from history."""
    ensure_spotify_init()
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"success": False, "error": "URL is required"}), 400
    
    try:
        playlist_history = load_history(PLAYLIST_HISTORY_FILE)
        playlist_history = [p for p in playlist_history if p["url"] != url]
        save_history(PLAYLIST_HISTORY_FILE, playlist_history)
        
        log_info(app_state, f"Playlist deleted from history: {url}")
        
        return jsonify({"success": True})
    except Exception as e:
        error_msg = str(e)
        log_error(app_state, f"Failed to delete playlist: {error_msg}")
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
    imports_dir = os.path.join(base_dir, "imported_tracks")
    if not os.path.isdir(imports_dir):
        return jsonify([])
    
    files = []
    for subdir_name in os.listdir(imports_dir):
        subdir_path = os.path.join(imports_dir, subdir_name)
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
        output_dir = os.path.join(base_dir, "generated_cards", f"{timestamp}_{sanitized_name}")
        
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
    try:
        from urllib.parse import unquote
        # Decode URL-encoded filename (handles spaces, etc.)
        decoded_filename = unquote(filename)
        
        # Handle nested paths (subdirectories)
        path_parts = decoded_filename.split('/')
        if len(path_parts) > 1:
            subdir = '/'.join(path_parts[:-1])
            filename_only = path_parts[-1]
            full_dir_path = os.path.join(base_dir, 'generated_cards', subdir)
        else:
            full_dir_path = os.path.join(base_dir, 'generated_cards')
            filename_only = decoded_filename
        
        # Verify the file exists
        full_file_path = os.path.join(full_dir_path, filename_only)
        if not os.path.exists(full_file_path):
            return f"File not found: {full_file_path}", 404
        
        return send_from_directory(full_dir_path, filename_only)
    except Exception as e:
        log_error(app_state, f"Error serving card file: {e}")
        return f"Error: {str(e)}", 500

@app.route('/api/cards/generated')
def get_generated_cards():
    """Get list of generated card sets."""
    ensure_spotify_init()
    try:
        generated_cards_dir = os.path.join(base_dir, "generated_cards")
        if not os.path.exists(generated_cards_dir):
            return jsonify([])
        
        card_sets = []
        for item in sorted(os.listdir(generated_cards_dir), reverse=True):
            item_path = os.path.join(generated_cards_dir, item)
            if os.path.isdir(item_path):
                files = []
                html_count = 0
                pdf_count = 0
                
                # Check for PDFs folder
                pdfs_dir = os.path.join(item_path, 'pdfs')
                pdfs_exist = os.path.exists(pdfs_dir) and os.path.isdir(pdfs_dir)
                
                for file in sorted(os.listdir(item_path)):
                    if file.endswith('.html'):
                        html_count += 1
                        # Check if PDF exists in pdfs subfolder
                        pdf_name = file.replace('.html', '.pdf')
                        pdf_path = os.path.join(pdfs_dir, pdf_name) if pdfs_exist else os.path.join(item_path, pdf_name)
                        has_pdf = os.path.exists(pdf_path)
                        
                        # Also check old location for backwards compatibility
                        if not has_pdf:
                            old_pdf_path = os.path.join(item_path, pdf_name)
                            has_pdf = os.path.exists(old_pdf_path)
                        
                        files.append({
                            "name": file,
                            "url": f"/generated_cards/{item}/{file}",
                            "type": "front" if "front" in file else "back",
                            "has_pdf": has_pdf,
                            "pdf_name": pdf_name if has_pdf else None
                        })
                
                # Count PDFs in pdfs folder
                if pdfs_exist:
                    pdf_count = len([f for f in os.listdir(pdfs_dir) if f.endswith('.pdf')])
                
                if files:
                    card_sets.append({
                        "name": item,
                        "path": item,
                        "files": files,
                        "count": html_count,
                        "pdf_count": pdf_count,
                        "has_all_pdfs": pdf_count == html_count and html_count > 0
                    })
        
        return jsonify(card_sets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cards/generate-pdfs', methods=['POST'])
def generate_pdfs():
    """Generate PDF files from HTML files in a card set directory."""
    ensure_spotify_init()
    try:
        try:
            from weasyprint import HTML
        except ImportError as e:
            error_msg = f"WeasyPrint is not installed. Install it: py -m pip install weasyprint (or activate venv first). Error: {str(e)}"
            log_error(app_state, error_msg)
            return jsonify({"success": False, "error": error_msg}), 500
        except OSError as e:
            # Windows-specific: Missing GTK+ libraries
            error_msg = (
                "WeasyPrint requires GTK3 Runtime on Windows.\n\n"
                "To install GTK3 Runtime:\n"
                "1. Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases\n"
                "2. Install GTK3 Runtime (MSYS2-based version)\n"
                "3. Restart the application\n\n"
                "Alternative: Use browser Print-to-PDF (Ctrl+P -> Save as PDF)"
            )
            log_error(app_state, f"WeasyPrint GTK error: {str(e)}")
            return jsonify({"success": False, "error": error_msg}), 500
        
        from urllib.parse import unquote
        
        data = request.json
        card_set_path = data.get('path')  # e.g., "20251116_115727_TuneTrack Apa"
        
        if not card_set_path:
            return jsonify({"success": False, "error": "Card set path not provided"}), 400
        
        # Decode URL-encoded path
        decoded_path = unquote(card_set_path)
        card_set_dir = os.path.join(base_dir, 'generated_cards', decoded_path)
        
        if not os.path.exists(card_set_dir) or not os.path.isdir(card_set_dir):
            return jsonify({"success": False, "error": f"Card set directory not found: {card_set_dir}"}), 404
        
        # Find all HTML files
        html_files = [f for f in sorted(os.listdir(card_set_dir)) if f.endswith('.html')]
        
        if not html_files:
            return jsonify({"success": False, "error": "No HTML files found in card set"}), 400
        
        # Create pdfs subfolder if it doesn't exist
        pdfs_dir = os.path.join(card_set_dir, 'pdfs')
        os.makedirs(pdfs_dir, exist_ok=True)
        
        generated_pdfs = []
        errors = []
        total_files = len(html_files)
        
        for idx, html_file in enumerate(html_files, 1):
            try:
                html_path = os.path.join(card_set_dir, html_file)
                pdf_file = html_file.replace('.html', '.pdf')
                # Save PDF in pdfs subfolder
                pdf_path = os.path.join(pdfs_dir, pdf_file)
                
                log_info(app_state, f"Generating PDF {idx}/{total_files}: {pdf_file}")
                
                # Read HTML content
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Convert to PDF using WeasyPrint
                # Use base_url to resolve relative paths (if any)
                html_doc = HTML(string=html_content, base_url=card_set_dir)
                
                # Generate PDF with A4 size and proper margins
                html_doc.write_pdf(
                    pdf_path,
                    stylesheets=None,  # CSS is already embedded in HTML
                )
                
                generated_pdfs.append(pdf_file)
                log_info(app_state, f"Generated PDF: {pdf_file} in pdfs/ folder")
                
            except ImportError as e:
                error_msg = f"WeasyPrint not available. Please install: pip install weasyprint"
                errors.append(error_msg)
                log_error(app_state, error_msg)
                break
            except Exception as e:
                error_msg = f"Error converting {html_file} to PDF: {str(e)}"
                errors.append(error_msg)
                log_error(app_state, error_msg)
        
        if errors and not generated_pdfs:
            return jsonify({"success": False, "error": "; ".join(errors)}), 500
        
        success_msg = f"Generated {len(generated_pdfs)} PDF file(s)"
        if errors:
            success_msg += f" ({len(errors)} error(s))"
        
        log_success(app_state, success_msg)
        
        return jsonify({
            "success": True,
            "generated": generated_pdfs,
            "errors": errors,
            "message": success_msg
        })
        
    except Exception as e:
        error_msg = str(e)
        log_error(app_state, f"Failed to generate PDFs: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), 500

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
    
    # Run with debug mode for auto-reload (development)
    # Disable Flask's template caching completely
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}
    app.run(host=host, port=port, debug=True, use_reloader=False)

if __name__ == '__main__':
    run_web_app()


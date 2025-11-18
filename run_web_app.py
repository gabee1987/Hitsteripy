"""
Launcher script for TuneGen Web App
Starts the Flask web server and opens browser automatically.
"""
import os
import sys
from pathlib import Path

# Add src to path
parent_dir = Path(__file__).parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from src.web_app import run_web_app

if __name__ == '__main__':
    run_web_app(host='127.0.0.1', port=5000, open_browser=True)


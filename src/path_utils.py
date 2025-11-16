"""
Utility functions for handling file paths in both development and PyInstaller environments.
"""
import os
import sys


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller.
    
    When running from PyInstaller, files are extracted to a temporary directory
    (sys._MEIPASS). This function returns the correct path in both scenarios.
    """
    # Check if running from PyInstaller
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        # Running normally (not from PyInstaller), use the current directory
        base_path = os.path.abspath(os.path.dirname(__file__))
        # Go up one level to get to project root
        base_path = os.path.dirname(base_path)
    
    full_path = os.path.join(base_path, relative_path)
    # Normalize path separators for Windows (handles mixed slashes)
    full_path = os.path.normpath(full_path)
    # Convert to absolute path to ensure it's always absolute
    full_path = os.path.abspath(full_path)
    return full_path


def get_template_path(filename):
    """Get the path to a template file."""
    return resource_path(os.path.join("templates", filename))


def get_asset_path(filename):
    """Get the path to an asset file."""
    return resource_path(os.path.join("assets", filename))


def get_data_path(filename):
    """Get the path to a data file in the current working directory."""
    # Data files should be in the working directory, not bundled
    return os.path.join(os.getcwd(), "data", filename)


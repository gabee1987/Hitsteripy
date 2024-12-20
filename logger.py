import sys

def log_info(message):
    """Log an informational message."""
    print(f"\033[94m[INFO] {message}\033[0m", file=sys.stdout)

def log_success(message):
    """Log a success message."""
    print(f"\033[92m[SUCCESS] {message}\033[0m", file=sys.stdout)

def log_error(message):
    """Log an error message."""
    print(f"\033[91m[ERROR] {message}\033[0m", file=sys.stderr)

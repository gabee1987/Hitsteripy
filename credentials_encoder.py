import base64
import os
from dotenv import load_dotenv

# Load environment variables from spotify.env
ENV_FILE = "spotify.env"

def load_credentials():
    """Load credentials from .env file."""
    if not os.path.exists(ENV_FILE):
        print("[ERROR] Environment file spotify.env not found.")
        exit(1)

    load_dotenv(ENV_FILE)

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("[ERROR] Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET in spotify.env.")
        exit(1)

    print(f"[DEBUG] Loaded credentials: {client_id}:{client_secret}")
    return client_id.strip(), client_secret.strip()

def encode_credentials(client_id, client_secret):
    """Generate Base64 encoded client credentials."""
    credentials = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    print(f"[DEBUG] Encoded credentials: {encoded}")
    return encoded

def decode_credentials(encoded_credentials):
    """Decode Base64 encoded credentials to verify correctness."""
    decoded_bytes = base64.b64decode(encoded_credentials.encode())
    decoded = decoded_bytes.decode()
    print(f"[DEBUG] Decoded credentials: {decoded}")
    return decoded

def validate_encoding(client_id, client_secret, encoded_credentials):
    """Validate if the encoding and decoding match the original credentials."""
    decoded = decode_credentials(encoded_credentials)
    expected = f"{client_id}:{client_secret}"
    if decoded == expected:
        print("[INFO] Encoding and decoding validation successful.")
        return True
    else:
        print("[ERROR] Validation failed!")
        print(f"[DEBUG] Expected: {expected}")
        print(f"[DEBUG] Got: {decoded}")
        return False

def compare_with_reference(reference_encoded):
    """Compare generated encoded credentials with a reference."""
    print("[INFO] Comparing encoded credentials with the reference...")
    client_id, client_secret = load_credentials()
    generated_encoded = encode_credentials(client_id, client_secret)
    if generated_encoded == reference_encoded:
        print("[SUCCESS] Encoded credentials match the reference.")
    else:
        print("[ERROR] Encoded credentials DO NOT match the reference.")
        print(f"[DEBUG] Generated: {generated_encoded}")
        print(f"[DEBUG] Reference: {reference_encoded}")

def main():
    print("[INFO] Starting credentials encoding and validation...")
    client_id, client_secret = load_credentials()
    encoded_credentials = encode_credentials(client_id, client_secret)
    
    # Validate the encoding process
    if not validate_encoding(client_id, client_secret, encoded_credentials):
        print("[ERROR] Encoding/decoding mismatch detected.")
        exit(1)

    # Compare with the working reference
    reference_encoded = "ZGZmNmFkNTQ4MmEwNDRiNWI3YTM4NjNiODkzNTQ5NjM6OTZlZWIzYjUwOWM4NDcxNmJlZjVjZjUxMDVmODlkM2Y="
    compare_with_reference(reference_encoded)

    print("[INFO] Encoding process completed successfully.")
    print(f"[RESULT] Encoded credentials: {encoded_credentials}")

if __name__ == "__main__":
    main()

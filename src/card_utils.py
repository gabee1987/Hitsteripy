import os
import csv
import io
import qrcode
import random
import base64
from jinja2 import Template
from .logger import log_info, log_error, log_success


def generate_qr_code(app_state, url, output_path):
    """Generate a QR code for a given URL and save to output_path."""
    try:
        img = qrcode.make(url)
        img.save(output_path)
        log_info(app_state, f"Generated QR code for {url} -> {output_path}")
    except Exception as e:
        log_error(app_state, f"Failed to generate QR code: {e}")


def generate_random_gradient():
    """
    Generate gradients with smooth, offset transitions and print-friendly colors.
    Colors are carefully selected for harmonious combinations.
    """
    # Define refined and harmonious color groups
    color_groups = [
        ["#E57373", "#F06292", "#BA68C8"],  # Rich pinks and purples
        ["#7986CB", "#64B5F6", "#4FC3F7"],  # Cool blues
        ["#81C784", "#AED581", "#DCE775"],  # Fresh greens and yellows
        ["#FFB74D", "#FF8A65", "#F06292"],  # Warm oranges and pinks
        ["#90A4AE", "#B0BEC5", "#CFD8DC"],  # Soft grays and blues
        ["#C5CAE9", "#7986CB", "#5C6BC0"],  # Muted purples and blues
        ["#FFCC80", "#FFAB91", "#FF8A65"],  # Warm peach and coral tones
        ["#4DB6AC", "#4DD0E1", "#81D4FA"],  # Cool teals and aquas
    ]

    # Pick a random color group
    color_group = random.choice(color_groups)

    # Use the selected colors to create a smooth gradient
    c1, c2, c3 = color_group

    # Randomize direction and offsets
    direction = random.randint(0, 360)
    offset1 = random.randint(-20, 20)  # Small shift for the first stop
    offset2 = random.randint(40, 60)  # Larger shift for the middle stop
    offset3 = random.randint(80, 100)  # End stop near the edge

    return f"linear-gradient({direction}deg, {c1} {offset1}%, {c2} {offset2}%, {c3} {offset3}%)"


def embed_image_as_base64(image_path):
    """Convert an image to a Base64 string for embedding in CSS."""
    try:
        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        raise FileNotFoundError(f"Could not embed image. Error: {e}")


def embed_css_with_background(css_path, background_image_path):
    """Embed the CSS file with an inline Base64 background image."""
    try:
        background_base64 = embed_image_as_base64(background_image_path)
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        # Replace the placeholder for the background image
        css_content = css_content.replace("../assets/card_bg_04.png", background_base64)
        return f"<style>\n{css_content}\n</style>"
    except Exception as e:
        raise FileNotFoundError(f"Could not embed CSS or image. Error: {e}")


def chunk_list(lst, size):
    """Utility: Yield successive chunks of size `size` from list `lst`."""
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

def generate_qr_data_uri(url):
    """Generate a QR code for `url` and return as a data URI (base64-encoded PNG)."""
    import qrcode
    import base64
    import io

    qr_img = qrcode.make(url)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def generate_html_cards(app_state, tracks_csv, output_dir):
    """
    Read tracks from CSV, chunk them in pages of 9 (or 12), and create multiple
    front/back HTML files: e.g. cards_front_page1.html, cards_back_page1.html, etc.

    Args:
        app_state (dict): Application state for logging.
        tracks_csv (str): Path to the input CSV file.
        output_dir (str): Path to the output directory.

    Returns:
        str: Summary message indicating successful generation.
    """
    # Paths to your template files
    front_template_path = os.path.join("templates", "cards_front_template.html")
    back_template_path = os.path.join("templates", "cards_back_template.html")
    css_path = os.path.join("templates", "cards.css")
    background_image_path = os.path.join("assets", "card_bg_04.png")

    # 1) Embed the CSS with background image as before
    embedded_css = embed_css_with_background(css_path, background_image_path)

    # 2) Read the tracks CSV and build up a track list
    all_tracks = []
    with open(tracks_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Instead of writing QR code to disk, let's embed them as data URIs
            qr_data_uri = generate_qr_data_uri(row["Spotify URL"])

            # Add random gradient
            row["gradient"] = generate_random_gradient()
            row["qr_data_uri"] = qr_data_uri
            row["serial_number"] = row["Serial Number"]
            row["artist"]       = row["Artist"]
            row["song_name"]    = row["Song Name"]
            row["year"]         = row["Year"]

            all_tracks.append(row)

    # 3) Load the Jinja2 templates *once*, for front and back
    with open(front_template_path, "r", encoding="utf-8") as f:
        front_template_str = f.read()
    front_template = Template(front_template_str)

    with open(back_template_path, "r", encoding="utf-8") as f:
        back_template_str = f.read()
    back_template = Template(back_template_str)

    # 4) Decide how many cards per page
    CARDS_PER_PAGE = 12  # a 3x4 arrangement

    # 5) Chunk the track list
    pages = list(chunk_list(all_tracks, CARDS_PER_PAGE))

    # 6) For each chunk -> generate a front HTML + back HTML
    page_count = len(pages)
    if page_count == 0:
        log_error(app_state, "No tracks found in CSV, nothing to generate.")
        return "No tracks to generate."

    # Prepare output
    for i, page_tracks in enumerate(pages, start=1):
        # Render front HTML for this chunk
        front_html = front_template.render(
            tracks=page_tracks,
            css_embedded=embedded_css,
            page_number=i,
            total_pages=page_count
        )
        # Render back HTML for this chunk
        back_html = back_template.render(
            tracks=page_tracks,
            css_embedded=embedded_css,
            page_number=i,
            total_pages=page_count
        )

        # Save each to a separate file
        front_file_name = f"cards_front_page{i}.html"
        back_file_name  = f"cards_back_page{i}.html"

        front_path = os.path.join(output_dir, front_file_name)
        back_path  = os.path.join(output_dir, back_file_name)

        with open(front_path, "w", encoding="utf-8") as f:
            f.write(front_html)
        with open(back_path, "w", encoding="utf-8") as f:
            f.write(back_html)

        log_info(app_state, f"Generated page {i} front/back: {front_file_name}, {back_file_name}")

    summary = f"{len(all_tracks)} tracks across {page_count} pages, saved in {output_dir}"
    log_success(app_state, summary)
    return summary

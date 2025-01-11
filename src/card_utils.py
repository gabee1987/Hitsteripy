import os
import csv
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


def generate_html_cards(app_state, tracks_csv, output_dir):
    """
    Generate front/back HTML cards with aligned grid layouts for printing.

    Args:
        app_state (dict): Application state for logging.
        tracks_csv (str): Path to the input CSV file.
        output_dir (str): Path to the output directory.

    Returns:
        str: Summary message indicating successful generation.
    """
    front_template_path = os.path.join("templates", "cards_front_template.html")
    back_template_path = os.path.join("templates", "cards_back_template.html")
    css_path = os.path.join("templates", "cards.css")
    background_image_path = os.path.join("assets", "card_bg_04.png")

    # Embed CSS with the background image
    embedded_css = embed_css_with_background(css_path, background_image_path)

    # Prepare the QR codes directory
    qr_dir = os.path.join(output_dir, "qrcodes")
    os.makedirs(qr_dir, exist_ok=True)

    # Process the tracks from the CSV file
    tracks = []
    with open(tracks_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            serial = row["Serial Number"]
            qr_filename = f"{serial}.png"
            qr_path = os.path.join(qr_dir, qr_filename)
            generate_qr_code(app_state, row["Spotify URL"], qr_path)

            row["qr_code"] = f"qrcodes/{qr_filename}"
            row["gradient"] = generate_random_gradient()
            row["serial_number"] = serial
            row["artist"] = row["Artist"]
            row["song_name"] = row["Song Name"]
            row["year"] = row["Year"]

            tracks.append(row)

    # Render the front and back HTML
    with open(front_template_path, "r", encoding="utf-8") as f:
        front_template = Template(f.read())
    with open(back_template_path, "r", encoding="utf-8") as f:
        back_template = Template(f.read())

    front_html = front_template.render(tracks=tracks, css_embedded=embedded_css)
    back_html = back_template.render(tracks=tracks, css_embedded=embedded_css)

    # Save the HTML files
    front_file_path = os.path.join(output_dir, "cards_front.html")
    back_file_path = os.path.join(output_dir, "cards_back.html")

    with open(front_file_path, "w", encoding="utf-8") as f:
        f.write(front_html)
    with open(back_file_path, "w", encoding="utf-8") as f:
        f.write(back_html)

    summary = f"HTML cards generated in {output_dir}"
    log_success(app_state, summary)
    return summary

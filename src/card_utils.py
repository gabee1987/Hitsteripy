import os
import csv
import io
import qrcode
import random
import base64
from jinja2 import Template
from .logger import log_info, log_error, log_success
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import SquareModuleDrawer  # Use square style

def generate_random_gradient():
    """
    Generate gradients with smooth, offset transitions and print-friendly colors.
    """
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
        # Replace the placeholder for the background image.
        css_content = css_content.replace("../assets/card_bg_06.png", background_base64)
        return f"<style>\n{css_content}\n</style>"
    except Exception as e:
        raise FileNotFoundError(f"Could not embed CSS or image. Error: {e}")

def chunk_list(lst, size):
    """Yield successive chunks of size `size` from list `lst`."""
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

def generate_custom_qr_data_uri(
        url,
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=4,
        border=2,
        fill_color="black",
        back_color=(255, 255, 255),  # White background as RGB tuple
        output_size=(150, 150)):
    """
    Generate a square QR code for `url` with a white background and customizable parameters.
    Returns a data URI (Base64-encoded PNG).

    Parameters:
      - url: The URL to encode.
      - version: QR Code version (1 to 40); if None, determined automatically.
      - error_correction: Error correction level.
      - box_size: Pixel size of each QR module.
      - border: Number of modules for the border.
      - fill_color: Color for the QR modules.
      - back_color: Background color (set to white as an RGB tuple).
      - output_size: Tuple (width, height) to resize the final image.

    Returns:
      A data URI (string) containing the Base64-encoded PNG of the generated QR code.
    """
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    import io, base64

    # Use SquareModuleDrawer by default for a standard square QR code.
    module_drawer = SquareModuleDrawer()
    
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction,
        box_size=box_size,
        border=border
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Generate the QR code image using StyledPilImage.
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=module_drawer,
        fill_color=fill_color,
        back_color=back_color
    ).convert("RGBA")
    
    # Optionally resize the image.
    if output_size is not None:
        img = img.resize(output_size, Image.LANCZOS)
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def generate_qr_data_uri(url):
    """
    Legacy function that generates a standard QR code as a data URI.
    Now calls generate_custom_qr_data_uri with default parameters.
    """
    return generate_custom_qr_data_uri(url)

def generate_html_cards(app_state, tracks_csv, output_dir):
    """
    Read tracks from CSV, chunk them into pages of 12 (3x4), and create multiple
    front/back HTML files.
    """
    front_template_path = os.path.join("templates", "cards_front_template.html")
    back_template_path = os.path.join("templates", "cards_back_template.html")
    css_path = os.path.join("templates", "cards.css")
    background_image_path = os.path.join("assets", "card_bg_06.png")
    
     # 1) Embed the CSS with background image as before
    embedded_css = embed_css_with_background(css_path, background_image_path)
    
     # 2) Read the tracks CSV and build up a track list
    all_tracks = []
    with open(tracks_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            qr_data_uri = generate_custom_qr_data_uri(
                row["Spotify URL"],
                box_size=4,
                border=2,
                fill_color="black",
                back_color=(255, 255, 255)  # White background
            )
            row["qr_data_uri"] = qr_data_uri
            row["gradient"] = generate_random_gradient()
            row["serial_number"] = row["Serial Number"]
            row["artist"] = row["Artist"]
            row["song_name"] = row["Song Name"]
            row["year"] = row["Year"]
            all_tracks.append(row)
    
    # 3) Load the Jinja2 templates *once*, for front and back
    with open(front_template_path, "r", encoding="utf-8") as f:
        front_template_str = f.read()
    front_template = Template(front_template_str)
    with open(back_template_path, "r", encoding="utf-8") as f:
        back_template_str = f.read()
    back_template = Template(back_template_str)
    
     # 4) Decide how many cards per page
    CARDS_PER_PAGE = 12  # 3x4 arrangement

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
        back_file_name = f"cards_back_page{i}.html"
        front_path = os.path.join(output_dir, front_file_name)
        back_path = os.path.join(output_dir, back_file_name)
        with open(front_path, "w", encoding="utf-8") as f:
            f.write(front_html)
        with open(back_path, "w", encoding="utf-8") as f:
            f.write(back_html)
        log_info(app_state, f"Generated page {i} front/back: {front_file_name}, {back_file_name}")
    
    summary = f"{len(all_tracks)} tracks across {page_count} pages, saved in {output_dir}"
    log_success(app_state, summary)
    return summary

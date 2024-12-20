import os
import qrcode
import random
from jinja2 import Template
import subprocess
from logger import log_info, log_error
from datetime import datetime

FRONT_TEMPLATE_FILE = "cards_front_template.html"
BACK_TEMPLATE_FILE = "cards_back_template.html"
CSS_FILE = "cards.css"

def generate_qr_code(url, output_path):
    """Generate a QR code for a given URL."""
    log_info(f"Generating QR code for URL: {url}")
    img = qrcode.make(url)
    img.save(output_path)
    log_info(f"QR code saved to {output_path}")

def generate_random_gradient():
    """Generate a valid random CSS gradient or fallback to a solid color."""
    supported_colors = [
        "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF", "#33FFF5",
        "#FFC300", "#DAF7A6", "#900C3F", "#581845"
    ]
    color1 = random.choice(supported_colors)
    color2 = random.choice(supported_colors)
    return f"{color1}"  # Fallback solid color for compatibility



def generate_html_and_pdf(tracks, output_dir):
    """Generate HTML and PDF files for the cards."""
    try:
        # Ensure required files are present
        for file in [FRONT_TEMPLATE_FILE, BACK_TEMPLATE_FILE, CSS_FILE]:
            if not os.path.exists(file):
                log_error(f"Missing required file: {file}")
                raise FileNotFoundError(file)

        # Create output directories
        qr_output_dir = os.path.join(output_dir, "qrcodes")
        os.makedirs(qr_output_dir, exist_ok=True)

        # Update QR code paths
        for track in tracks:
            old_qr_path = track["qr_code"]
            new_qr_path = os.path.join(qr_output_dir, os.path.basename(old_qr_path))
            os.replace(old_qr_path, new_qr_path)  # Move QR codes to output directory
            track["qr_code"] = f"file:///{os.path.abspath(new_qr_path).replace(os.sep, '/')}"

        # Load templates
        with open(FRONT_TEMPLATE_FILE, "r", encoding="utf-8") as f:
            front_template = Template(f.read())
        with open(BACK_TEMPLATE_FILE, "r", encoding="utf-8") as f:
            back_template = Template(f.read())

        # Add random gradients to tracks
        for track in tracks:
            track["gradient"] = generate_random_gradient()

        # Render HTML
        css_path = f"file:///{os.path.abspath(CSS_FILE).replace(os.sep, '/')}"
        front_html = front_template.render(tracks=tracks, css_file=css_path)
        back_html = back_template.render(tracks=tracks, css_file=css_path)

        # Save HTML files
        front_html_path = os.path.join(output_dir, "cards_front.html")
        back_html_path = os.path.join(output_dir, "cards_back.html")
        with open(front_html_path, "w", encoding="utf-8") as f:
            f.write(front_html)
        with open(back_html_path, "w", encoding="utf-8") as f:
            f.write(back_html)

        # Generate PDFs
        log_info("Generating PDFs...")
        front_pdf_path = os.path.join(output_dir, "output_front.pdf")
        back_pdf_path = os.path.join(output_dir, "output_back.pdf")
        subprocess.run(["weasyprint", front_html_path, front_pdf_path], check=True)
        subprocess.run(["weasyprint", back_html_path, back_pdf_path], check=True)
        log_info(f"PDFs generated: {front_pdf_path}, {back_pdf_path}")
    except Exception as e:
        log_error(f"Error generating HTML and PDF: {e}")
        raise

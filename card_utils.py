import os
import qrcode
import random
from jinja2 import Template
import subprocess
from logger import log_info, log_error

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
    """Generate a random vibrant gradient for card backgrounds."""
    h1, s1, l1 = random.randint(0, 360), 100, random.randint(50, 70)
    h2, s2, l2 = random.randint(0, 360), 100, random.randint(50, 70)
    color1 = f"hsl({h1}, {s1}%, {l1}%)"
    color2 = f"hsl({h2}, {s2}%, {l2}%)"
    return f"linear-gradient(45deg, {color1}, {color2})"

def generate_html_and_pdf(tracks):
    """Generate HTML and PDF files for the cards."""
    try:
        # Ensure required files are present
        if not os.path.exists(FRONT_TEMPLATE_FILE):
            log_error(f"Missing required template file: {FRONT_TEMPLATE_FILE}")
            exit(1)
        if not os.path.exists(BACK_TEMPLATE_FILE):
            log_error(f"Missing required template file: {BACK_TEMPLATE_FILE}")
            exit(1)
        if not os.path.exists(CSS_FILE):
            log_error(f"Missing required CSS file: {CSS_FILE}")
            exit(1)

        with open(FRONT_TEMPLATE_FILE, "r", encoding="utf-8") as f:
            front_template = Template(f.read())

        with open(BACK_TEMPLATE_FILE, "r", encoding="utf-8") as f:
            back_template = Template(f.read())

        # Add random gradients to tracks
        for track in tracks:
            track["gradient"] = generate_random_gradient()

        front_html = front_template.render(tracks=tracks, css_file=CSS_FILE)
        back_html = back_template.render(tracks=tracks, css_file=CSS_FILE)

        with open("cards_front.html", "w", encoding="utf-8") as f:
            f.write(front_html)
        with open("cards_back.html", "w", encoding="utf-8") as f:
            f.write(back_html)

        log_info("Generating PDFs...")
        subprocess.run(["weasyprint", "cards_front.html", "output_front.pdf"], check=True)
        subprocess.run(["weasyprint", "cards_back.html", "output_back.pdf"], check=True)
        log_info("PDF generation completed.")
    except Exception as e:
        log_error(f"Error generating HTML and PDF: {e}")
        raise

#!/usr/bin/env python3
"""
images_to_pdf.py

Convert multiple image files into a single multi-page PDF.

Usage:
    images_to_pdf.py [OPTIONS] <image files | directory | zipfile>

Examples:
    # Combine specific image files into a PDF
    ./images_to_pdf.py img1.jpg img2.jpg -o out.pdf

    # Convert all images in a directory to a PDF
    ./images_to_pdf.py my_images_dir/ -o output.pdf

    # Unpack a ZIP file and convert its images to a PDF
    ./images_to_pdf.py images.zip

Options:
    -o, --output FILE     Output PDF filename (default: output.pdf)
    --dpi DPI             Output resolution in DPI (default: 150)

Supported image formats: JPG, PNG, BMP, TIFF
"""

import argparse
import logging
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image  # pip install Pillow

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("images_to_pdf")

def extract_zip(zip_path):
    temp_dir = tempfile.TemporaryDirectory()
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(temp_dir.name)
        logger.info(f"Extracted ZIP file '{zip_path}' to temporary directory.")
    except zipfile.BadZipFile as e:
        logger.error(f"Invalid ZIP file: {zip_path}: {e}")
        sys.exit(1)
    return temp_dir

def collect_image_files(source):
    supported_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    if isinstance(source, list):
        files = [Path(f) for f in source]
    else:
        files = [f for f in Path(source).rglob('*') if f.suffix.lower() in supported_exts]
    return sorted(files, key=lambda p: p.name.lower())

def convert_images_to_pdf(images, output_file, dpi):
    pil_images = []
    for img_path in images:
        try:
            img = Image.open(img_path).convert('RGB')
            pil_images.append(img)
        except Exception as e:
            logger.warning(f"Skipping file '{img_path}': {e}")
    if not pil_images:
        logger.error("No valid images found to convert.")
        sys.exit(1)
    try:
        pil_images[0].save(output_file, save_all=True, append_images=pil_images[1:], dpi=(dpi, dpi))
        logger.info(f"PDF saved to '{output_file}'")
    except Exception as e:
        logger.error(f"Failed to save PDF: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Convert images to a multi-page PDF.")
    parser.add_argument("input", nargs='+', help="Image files, a directory, or a zip file.")
    parser.add_argument("-o", "--output", default="output.pdf", help="Output PDF file name.")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for the output PDF (default: 150).")

    args = parser.parse_args()

    image_files = []
    temp_dirs = []

    for inp in args.input:
        p = Path(inp)
        if p.is_file() and p.suffix.lower() == '.zip':
            temp_dir = extract_zip(p)
            temp_dirs.append(temp_dir)
            image_files.extend(collect_image_files(temp_dir.name))
        elif p.is_dir():
            image_files.extend(collect_image_files(p))
        elif p.is_file():
            image_files.append(p)
        else:
            logger.warning(f"Skipping unrecognized input: '{inp}'")

    image_files = sorted(
        [f for f in image_files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']],
        key=lambda x: x.name.lower()
    )

    convert_images_to_pdf(image_files, args.output, args.dpi)

    for td in temp_dirs:
        td.cleanup()

if __name__ == "__main__":
    main()

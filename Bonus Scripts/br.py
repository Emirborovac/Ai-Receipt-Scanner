import cv2
import numpy as np
from pyzbar.pyzbar import decode
import barcode
from barcode.writer import ImageWriter
import os

def detect_and_generate_barcode(image_path, output_path="generated_barcode.png"):
    # Load the image
    image = cv2.imread(image_path)

    # Convert to grayscale for better barcode detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect barcodes using pyzbar
    barcodes = decode(gray)

    # If barcode is detected, regenerate it as a new barcode image
    for barcode_data in barcodes:
        barcode_text = barcode_data.data.decode("utf-8")
        print(f"Detected Barcode: {barcode_text}")  # Print barcode data

        # Generate barcode without text
        barcode_type = "code128"  # Modify if needed (EAN13, etc.)
        generated_barcode = barcode.get_barcode_class(barcode_type)(
            barcode_text, writer=ImageWriter()
        )

        # Save barcode without numbers below
        generated_barcode.save(output_path.replace(".png", ""), {"write_text": False})

        print(f"Generated barcode saved as: {output_path}")

# Example usage
image_path = "20250215_170824.jpg"  # Replace with your image file
detect_and_generate_barcode(image_path, "output_barcode.png")

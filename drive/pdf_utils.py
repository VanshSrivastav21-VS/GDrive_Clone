from pdf2image import convert_from_path
import os
from django.conf import settings
from PIL import Image

def pdf_to_image(pdf_path, output_path, dpi=100):
    images = convert_from_path(pdf_path, dpi=dpi)
    if images:
        # Save the first page as an image
        images[0].save(output_path, 'PNG')
    else:
        # Return a default image if no pages are found
        Image.new('RGB', (100, 100), color=(255, 255, 255)).save(output_path, 'PNG')

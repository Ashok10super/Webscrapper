import requests
from requests.adapters import HTTPAdapter, Retry
from PIL import Image,ImageEnhance
from io import BytesIO
import numpy as np
import pytesseract
import cv2


def extract_text(url):
    # Create a session with retries
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://",HTTPAdapter(max_retries=retries))
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    try:
        # Fetch the image
        response = session.get(url, stream=True)
        response.raise_for_status()

        # Open the image using PIL
        img = Image.open(BytesIO(response.content))

         #pass the image to the encahncer function to pre-process the image before passing it to the tessaract
        processed_image = image_enchancer(image=img)

        custom_config = r'--psm 6' 

        # Perform OCR using pytesseract
        text = pytesseract.image_to_string(processed_image,lang='eng',config=custom_config)
        
        # Return the extracted text
        return text

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def image_enchancer(image):
 contrast = ImageEnhance.Contrast(image=image)
 enchanced_image = contrast.enhance(1.5)
 return enchanced_image

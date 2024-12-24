import requests
from requests.adapters import HTTPAdapter, Retry
from PIL import Image
from io import BytesIO
import pytesseract


def extract_text(url):
    # Create a session with retries
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        # Fetch the image
        response = session.get(url, stream=True)
        response.raise_for_status()

        # Open the image using PIL
        img = Image.open(BytesIO(response.content))

        # Perform OCR using pytesseract
        text = pytesseract.image_to_string(img)

        # Return the extracted text
        return text

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

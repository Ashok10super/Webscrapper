from PIL import ImageEnhance
import pytesseract
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from PIL import Image
from io import BytesIO
from eauctionsindiabot.custom_exceptions.exceptions import TesseractOCRError
def extract_text(url, session):
    try:
        response = session.get(url, stream=True)
        response.raise_for_status()
    except Exception as e:
        raise TesseractOCRError(e) from e
    try:
        # Fetch the image
        response = session.get(url, stream=True)
        response.raise_for_status()

        # Open the image using PIL
        img = Image.open(BytesIO(response.content))

        # Pre-process the image before OCR
        processed_image = image_enchancer(image=img)

        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(get_text_from_image, processed_image)
            text = future.result(timeout=30)

    except TimeoutError as e:
        print("OCR process took too long. Killing it.")
        future.cancel()
        text = "Sale-notice is complex to read"
    except Exception as e:
        print(f"OCR failed with error: {e}")
        text = "Sale-notice OCR error"
        raise TesseractOCRError(e) from e
    return text



def get_text_from_image(processed_image):
        # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        custom_config = r'--psm 3'
        # Perform OCR using pytesseract
        text = "Sale-notice is complex to read"  # <-- FIX: Initialize text as None
        try:
            text = pytesseract.image_to_string(processed_image, lang='eng', config=custom_config, timeout=15)
        except RuntimeError as e:
                print("Tesseract OCR timed out:", e)
                pass
        # Return the extracted text
        return text

def image_enchancer(image):
 contrast = ImageEnhance.Contrast(image=image)
 enchanced_image = contrast.enhance(1.5)
 return enchanced_image

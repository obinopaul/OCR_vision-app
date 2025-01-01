import pytesseract
from transformers import pipeline
import ollama
import os
import easyocr
import cv2
import numpy as np
from PIL import Image

# Tesseract OCR Path (Modify for your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize EasyOCR Reader
_easyocr_reader = None

def get_easyocr_reader():
    """Load and cache the EasyOCR reader."""
    global _easyocr_reader
    if _easyocr_reader is None:
        _easyocr_reader = easyocr.Reader(["en"], gpu=True)  # Add other languages if needed
    return _easyocr_reader



# Perform OCR with Selected Vision Model
def perform_ocr_with_model(image, model_name, uploaded_file):
    if model_name == "tesseract":
        return perform_tesseract_ocr(image)
    elif model_name == "easyocr":
        return perform_easyocr(image)
    elif model_name == "llama3.2.vision:latest":
        return perform_llama_vision_ocr(uploaded_file)
    elif model_name == "custom-vision":
        return "Custom Vision model is not yet implemented."
    else:
        return "Unknown model selected."


def perform_tesseract_ocr(image):
    """Perform OCR using Tesseract."""
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error with Tesseract OCR: {e}"


def perform_easyocr(image):
    """Perform OCR using EasyOCR."""
    try:
        # Convert PIL image to OpenCV format
        image_np = np.array(image)
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        # Perform OCR
        reader = get_easyocr_reader()
        results = reader.readtext(image_cv)

        # Combine extracted text
        extracted_text = "\n".join([text for _, text, _ in results])
        return extracted_text if extracted_text else "No text detected with EasyOCR."
    except Exception as e:
        return f"Error with EasyOCR: {e}"


# def perform_llama_vision_ocr(image):
#     """ Perform OCR using LLaMA3 Vision pipeline. """
#     # Simulated LLaMA3 Vision pipeline for example purposes
#     try:
#         vision_pipeline = pipeline("image-to-text", model="llama3-vision")
#         text = vision_pipeline(image)
#         return text[0]["generated_text"]
#     except Exception as e:
#         return f"Error: {e}"

def perform_llama_vision_ocr(image):
    """ Perform OCR using LLaMA3 Vision pipeline. """
    # Simulated LLaMA3 Vision pipeline for example purposes
    try:
        response = ollama.chat(
                        model='llama3.2-vision:latest',
                        messages=[{
                            'role': 'user',
                            'content': """Analyze the text in the provided image. Extract all readable content
                                        and present it in a structured Markdown format that is clear, concise, 
                                        and well-organized. Ensure proper formatting (e.g., headings, lists, or
                                        code blocks) as necessary to represent the content effectively.""",
                            'images': [image.getvalue()]
                        }]
                    )
        return response.message.content
    except Exception as e:
        return f"Error: {e}"
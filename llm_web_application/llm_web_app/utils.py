import mimetypes
import chardet
from PyPDF2 import PdfReader
from docx import Document
from pdfminer.high_level import extract_text
import pymupdf
import google.generativeai as genai
import os
import io
from pdf2image import convert_from_bytes
from io import BytesIO
from PIL import Image , ImageEnhance, ImageFilter
import cv2
import pytesseract
import numpy as np
from goose3 import Goose
from dotenv import load_dotenv
load_dotenv()

def get_file_mime_type(inner_file_path):
    mime_type, _ = mimetypes.guess_type(inner_file_path)
    return mime_type

def process_file(file_path):
    mime_type = get_file_mime_type(file_path)
    print(f"File MIME type: {mime_type}")
    FileTexts = ""

    if mime_type == 'application/pdf':
        # Handle PDF files with PDFMiner
        try:
            doc = pymupdf.open(file_path)
            for page in doc: # iterate the document pages
                FileTexts += page.get_text() # get plain text encoded as UTF-8
            print("Document Text outter: " , len(FileTexts))
            if len(FileTexts.strip())==0:
                print("Text processing started")
                FileTexts = pdf_to_page_extract(file_path)
                print("Document Text inner: " , FileTexts)
        except Exception as e:
            print(f"An error occurred while processing PDF: {e}")
            FileTexts = "Error reading PDF file."
    elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        # Handle DOCX files
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                FileTexts += para.text + "\n"
        except Exception as e:
            print(f"An error occurred while processing DOCX: {e}")
            FileTexts = "Error reading DOCX file."

    elif mime_type in ['text/plain', 'application/x-tex', 'application/xml']:
        # Handle text files
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                content = raw_data.decode(encoding)
                FileTexts = content
        except UnicodeDecodeError:
            FileTexts = "Error decoding file with detected encoding."
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            FileTexts = "Error reading file."

    else:
        FileTexts = "Unsupported file type or unable to determine MIME type."


    print("File Processing complete\n")
    print("================================Text================================")
    print(FileTexts)
    # if FileTexts is empty then call image processing and extract text from the file
    



    return FileTexts
#---------------------------------------------------------------- When PDF parsing is not possible ----------------------------------------------------------------


# def pdf_to_page_extraction(file_data):
    try:
        pages = convert_from_bytes(file_data)
        images_text = ""
        info=""
        for page in pages:
            with BytesIO() as image_stream:
                page.save(image_stream, format='JPEG')
                image_stream.seek(0)
                page_text , page_info = image_to_text_with_gimini(image_stream.getvalue())
                # Concatenate the extracted text and info
                images_text += page_text
                info += page_info
        return images_text , info
    except Exception as e:
        print(f"Error extracting text from PDF images: {e}")
        return ""
# -----------------------------Image to text extraction function-----------------------------------------------
# Way: 1
# def extract_text_from_image_only(image_data):
#     image = Image.open(io.BytesIO(image_data))
#     image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)  # Convert to BGR format for OpenCV
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     denoised = cv2.fastNlMeansDenoising(binary, None, 30, 7, 21)
#     text = pytesseract.image_to_string(image)
#     return text


# Way : 2

def pdf_to_page_extract(file_path):
    print("path: ", file_path)
    try:
        # Open the file in binary mode and read its content as bytes
        with open(file_path, 'rb') as pdf_file:
            file_bytes = pdf_file.read()
        
        # Convert PDF bytes to images
        pages = convert_from_bytes(file_bytes)
        images_text = ""
        
        # Extract text from each page image
        for page in pages:
            with BytesIO() as image_stream:
                page.save(image_stream, format='JPEG')
                image_stream.seek(0)
                images_text += extract_text_from_image(image_stream.getvalue())
        
        return images_text
    except Exception as e:
        print(f"Error extracting text from PDF images: {e}")
        return ""
def adjust_brightness_contrast(image, alpha, beta):
    return cv2.addWeighted(image, alpha, image, 0, beta)

def extract_text_from_image(image_data):
    # Load image from bytes and convert to OpenCV format
    image = Image.open(io.BytesIO(image_data))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)  # Convert to BGR format for OpenCV

    enhanced_image = adjust_brightness_contrast(image, 1, 5)

    # Extract text from the preprocessed image
    text = pytesseract.image_to_string(enhanced_image, lang = 'eng+ben')
    return text

# # Gimini API Call
# import google.generativeai as genai
# API_KEY="AIzaSyDnL3F7x_xh-BYsx_144N06FHBKhDTFCCc"
# genai.configure(api_key= API_KEY)

# def image_to_text_with_gimini(image_data):
#     # Load image from bytes and convert to OpenCV format
#     image = Image.open(io.BytesIO(image_data))
#     model = genai.GenerativeModel(model_name="gemini-1.5-flash")
#     response1 = model.generate_content(["Extract Full Text without Special", image])

#     response2 = model.generate_content(["Extract All Information", image])
#     return response1.text , response2.text


# ---------------------------------------------------------------- end of the function ----------------------------------------------------------------
# Gemini API call
# API_KEY = os.getenv('GEMINI_API_KEY')
API_KEY= "AIzaSyDsoucWf1SUnD0k6KMWzHEfnQI6hGx6_-k"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def gemini_llm_api(context: str) -> str:
    try:
        response = model.generate_content(context)
        print(response.text)
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return "An error occurred while generating the answer."

def TextSummarization(text_data):
    query ="Summarize the entire context comprehensively, highlighting all important details in a narrative format  the use of bullet points"
    # Construct a refined context prompt
    context = (
        f"please answer the following question. Ensure your response is precise and focused on the query.\n\n"
        f"Question:\n{query}\n\n"
        f"Context:\n{text_data}\n\n"
        f"Provide a clear and concise answer based only on the context above."
    )
    summarizeText= gemini_llm_api(context)
    return summarizeText


# def ComparativeAnalysis(documents_1 , documents_2):
#     query ="comparative analysis of documents using  the provided documents_1 and documents_2 "
#     # Construct a refined context prompt
#     context = (
#         f"please answer the following question. Ensure your response is precise and focused on the query.\n\n"
#         f"Question:\n{query}\n\n"

#         f"Context (document 1):\n{documents_1}\n\n"
#         f"Context (document 2):\n{documents_2}\n\n"

#         f"Provide a clear and concise answer based only on the context above."
#     )
#     ComparativeText= gemini_llm_api(context)
#     return ComparativeText

def ComparativeAnalysis(documents_1, documents_2):
    query = (
        "Conduct a detailed comparative analysis of the provided documents with a focus on policy alignment. "
        "Identify and highlight the most important information from each documents"
        "Provide comparative insights based on these findings, and discuss the implications of the similarities and differences in the context."
    )
    
    # Construct a refined context prompt
    context = (
        f"Please perform a comparative analysis based on the following query:\n\n"
        f"Query:\n{query}\n\n"

        f"Context (Document 1):\n{documents_1}\n\n"
        f"Context (Document 2):\n{documents_2}\n\n"

        f"Your analysis should include:\n"
        f"1. Important information each document.\n"
        f"3. A comparative evaluation of key points of alignment and divergence.\n"
        f"4. Insights that discuss the implications of these findings in relation to the broader policy objectives."
    )
    
    ComparativeText = gemini_llm_api(context)
    return ComparativeText



def extract_article_content(url):
    go=Goose()
    content= go.extract(url)
    return content

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
import fitz  # PyMuPDF

from transformers import pipeline
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS  # Updated import
from langchain.text_splitter import CharacterTextSplitter

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
            print(f"Document Length: {len(doc)}")
            for page in doc: # iterate the document pages
                FileTexts += page.get_text() # get plain text encoded as UTF-8
            print("Document Text length: " , len(FileTexts))
            if len(FileTexts.strip())==0:
                print("Text processing started")
                FileTexts = pdf_to_page_extract(file_path)
                print("Document Text demo: " , FileTexts[10])
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
    # print(FileTexts)
    # if FileTexts is empty then call image processing and extract text from the file
    



    return FileTexts
#---------------------------------------------------------------- When PDF parsing is not possible ----------------------------------------------------------------


# ======================================================== Image to text extraction function =================================================================



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


# ======================================================== end of the function =================================================================


# ================================================================== Gemini API call========================================================================
# API_KEY = os.getenv('GEMINI_API_KEY')
API_KEY= "AIzaSyDsoucWf1SUnD0k6KMWzHEfnQI6hGx6_-k"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def gemini_llm_api(context: str) -> str:
    try:
        response = model.generate_content(context)
        print("Gemini Response:: " , response.text)
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return "An error occurred while generating the answer."
    

# ======================================================== For Huggingface Text Summarization and QA =================================================================

# Initialize the Hugging Face pipeline for text generation with FLAN-T5
gen_pipeline = pipeline('text2text-generation', model='google/flan-t5-large')
summarization_pipeline = pipeline('summarization', model='google/flan-t5-large')

def manual_text_splitter(text, chunk_size=500, chunk_overlap=100):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        # Move start forward by the chunk size minus the overlap to avoid reprocessing
        start += chunk_size - chunk_overlap
        print(start, end)
    return chunks


def answer_manipulation(query_type, doc1_answers, doc2_answers):
    # Define key points for each query type
    queries = {
        "matching": [
            "Goals and objectives",
            "Timeline and milestones",
            "Key focus areas",
            "Enhancing effectiveness",
            "Anticipated challenges",
            "Leveraging programs and initiatives",
            "New initiatives or changes",
            "Addressing gaps",
            "Opportunities for collaboration",
            "Ethical considerations and governance"
        ],
        "inconsistencies": [
            "Discrepancies between objectives and actions",
            "Alignment of implementation approach with goals",
            "Internal or cross-sectional policy conflicts",
            "Governance and ethical inconsistency",
            "Handling of international collaboration and conflicts"
        ],
        "enhancements": [
            "Overlapping objectives and approaches",
            "Potential conflicts in timeline and implementation",
            "Maximizing impact through initiatives",
            "Opportunities for internal collaborations",
            "Integration of best practices",
            "Incorporating international standards and practices",
            "Recommendations for improving governance and ethics",
            "Development programs for policy enhancement",
            "Standardization of data-sharing frameworks",
            "Aligning ethical frameworks with best practices"
        ]
    }

    key_points = queries.get(query_type, [])
    synthesized_responses = []
    # Define headers for each type of query
    headers = {
    "matching": "## Alignment of New Policy with Existing Policies, Programs, and Projects",
    "inconsistencies": "## Identifying Inconsistencies Between New Policy and Existing Frameworks",
    "enhancements": "## Enhancing and Integrating New Policy with Existing Policies and Programs"
    }

    header = headers.get(query_type, "")


    for i, key_point in enumerate(key_points):
        if i < len(doc1_answers[query_type]) and i < len(doc2_answers[query_type]):
            if query_type == "matching":
                synthesis = (
                    f"**{key_point}:** New Policy emphasizes **{doc1_answers[query_type][i]}**, while Existing policy highlights **{doc2_answers[query_type][i]}**. "
                    "Together, these points show a balance between specific goals and broad strategies, with a focus on collaboration and effectiveness."
                )
            elif query_type == "inconsistencies":
                synthesis = (
                    f"**{key_point}:** New Policy notes **{doc1_answers[query_type][i]}**, and Existing policy highlights **{doc2_answers[query_type][i]}**. "
                    "These inconsistencies point to discrepancies in objectives, implementation challenges, and potential gaps in ethical frameworks."
                )
            elif query_type == "enhancements":
                synthesis = (
                    f"**{key_point}:** New Policy suggests **{doc1_answers[query_type][i]}**, while Existing policy proposes **{doc2_answers[query_type][i]}**. "
                    "Both documents provide insights into areas for integrating best practices, addressing conflicts, and improving policy effectiveness."
                )
            synthesized_responses.append(synthesis)
        else:
            synthesized_responses.append(f"{key_point}: Information not available in one or both documents.")
    
    # Join all synthesized responses into a single string separated by newlines
    final_synthesis = f"{headers.get(query_type, '')}\n\n" + "\n\n".join(synthesized_responses)

    print("FINAL SYN::" , final_synthesis)
    print("\n\n")

    return final_synthesis


def rag_for_huggingface_qa(base_query, doc_text_1, doc_text_2):
    # Step 1: Define sub-questions based on the main query
    subquestions_based_query = []
    key=''

    if base_query == "How is the new policy matching with other existing policies, programs, and projects?":
        key='matching'
        sub_questions = [
            "What are the primary goals and objectives of this policy?",
            "How is the timeline of this policy structured and what milestones are outlined?",
            "What are the key areas of focus within this policy?",
            "How does this policy propose to enhance its effectiveness?",
            "What challenges are anticipated in implementing this policy?",
            "What strategies does this policy suggest for leveraging its own programs and initiatives?",
            "In what specific areas does this policy propose new initiatives or changes?",
            "How does this policy address any gaps identified within its own scope?",
            "What opportunities for internal improvement or collaboration does this policy identify?",
            "How are the ethical considerations and governance frameworks addressed within this policy?"
        ]
        subquestions_based_query.extend(sub_questions)

    elif base_query == "What are the inconsistencies of the new policy with other existing policies, programs, and projects?":
        key='inconsistencies'
        sub_questions = [
            "Are there any discrepancies between the stated objectives and the proposed actions?",
            "How does the policy’s implementation approach align with its stated goals?",
            "What are the potential conflicts within the policy’s own framework or between different sections?",
            "Are there any inconsistencies in the policy’s approach to governance and ethical considerations?",
            "How does the policy handle international collaboration, and are there any conflicting elements?"
        ]
        subquestions_based_query.extend(sub_questions)

    elif base_query == "How can we enhance or integrate the new policy with the existing policies, programs, and projects?":
        key='enhancements'
        sub_questions = [
            "What are the overlapping objectives and approaches within this policy?",
            "What potential conflicts might arise within the policy itself, especially regarding its timeline and implementation?",
            "How can the policy leverage its own initiatives to maximize impact?",
            "What opportunities are there for internal projects and collaborations within the policy’s scope?",
            "How can best practices be integrated into the policy’s framework?",
            "How can international standards and practices be incorporated into this policy?",
            "What specific recommendations can be made to improve the policy’s framework in key areas such as governance and ethics?",
            "What development programs could help enhance the policy’s effectiveness?",
            "How can data-sharing frameworks be standardized within the policy for better implementation?",
            "What steps can be taken to align the policy’s ethical frameworks with best practices?"
        ]
        subquestions_based_query.extend(sub_questions)

    print("Text Splitting Done!!")
    # Split both documents into chunks
    chunks_doc_text_1 = manual_text_splitter(doc_text_1, chunk_size=1000, chunk_overlap=200)
    chunks_doc_text_2 = manual_text_splitter(doc_text_2, chunk_size=1000, chunk_overlap=200)


    # Step 3: Create embeddings and vector stores
    embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    vector_store_doc_text_1 = FAISS.from_texts(chunks_doc_text_1, embedding_model)
    vector_store_doc_text_2 = FAISS.from_texts(chunks_doc_text_2, embedding_model)
    print("Vector Store Setup Done!!")
    # Step 4: Chunk retrieval from documents
    retriever_doc_text_1 = vector_store_doc_text_1.as_retriever()
    retriever_doc_text_2 = vector_store_doc_text_2.as_retriever()
    print("Retrieval Setup Done!!")
    combined_answers = []
    doc1_answers={key:[]}
    doc2_answers={key:[]}
    for query in subquestions_based_query:
        # Retrieve relevant documents
        docs_doc_text_1 = retriever_doc_text_1.invoke(query)
        docs_doc_text_2 = retriever_doc_text_2.invoke(query)
              

        # Combine context from retrieved documents
        combined_context_doc_text_1 = docs_doc_text_1[0].page_content
        combined_context_doc_text_2 = docs_doc_text_2[0].page_content

        # Step 5: Generate answers using a text generation pipeline
        input_text_doc_text_1 = f"query: {query} context: {combined_context_doc_text_1}"
        input_text_doc_text_2 = f"query: {query} context: {combined_context_doc_text_2}"

        # Generate answers using the text generation pipeline
        answer_doc_text_1 = gen_pipeline(input_text_doc_text_1)[0]['generated_text']
        answer_doc_text_2 = gen_pipeline(input_text_doc_text_2)[0]['generated_text']

        doc1_answers[key].append(answer_doc_text_1)
        doc2_answers[key].append(answer_doc_text_2)

    # # Step 6: Return the final combined answer
    final_answer = answer_manipulation(key, doc1_answers, doc2_answers)
    # Call the answer_manipulation function with collected answers
    return final_answer


def huggingface_llm_api_for_summarization(context):
    # Initialize the summarization pipeline
    # summarization_pipeline = pipeline('summarization', model='google/flan-t5-large')

    # Determine the chunk size dynamically based on context length
    context_length = len(context)
    
    # Dynamically set chunk size based on context length
    if context_length <= 3000:
        max_chunk_size = 512
    elif context_length <= 6000:
        max_chunk_size = 768
    else:
        max_chunk_size = 1024  # Larger chunk size for very large contexts

    # Break down the context into chunks of the determined size
    chunks = [context[i:i + max_chunk_size] for i in range(0, context_length, max_chunk_size)]
    
    # Summarize each chunk and combine the results
    summaries = []
    try:
        for chunk in chunks:
            summary = summarization_pipeline(chunk, max_length=150, min_length=50, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        
        # Combine the summaries into a single summary
        final_summary = " ".join(summaries)
        return final_summary

    except Exception as e:
        return f"An error occurred during summarization: {str(e)}"


#================================================================ ChatGPT API Model Implementation =================================================================

def chatgpt_llm_api(context):

    return "GPT model not yet available"


#================================================================ End of all model =================================================================================

# =============================================================== Text Summarization =======================================================


def TextSummarization(model , text_data):
    query ="Summarize the entire context comprehensively, extract all important details in a narrative format  the use of proper markdown syntax and newline characters"
    # Construct a refined context prompt
    context = (
        f"please answer the following question. Ensure your response is precise and focused on the query.\n\n"
        f"Question:\n{query}\n\n"
        f"Context:\n{text_data}\n\n"
        f"Provide a clear and concise answer based only on the context above."
    )

    if model == "gemini":
        return gemini_llm_api(context)
    elif model == "huggingface":
        return huggingface_llm_api_for_summarization(context)
    elif model == "chatgpt":
        return chatgpt_llm_api(context)
    else:
        return "Invalid model name provided."


# =============================================================== QA  =======================================================

def ComparativeAnalysis(model, question, own_file_text, existing_file_text):
    # Prepare the base query structure
    base_query = (
        "Analyze the following question based on the provided documents. Your response should be clear and well-structured with markdown format.\n\n"
        f"**Question:** {question}\n\n"
        f"**New Policy Document:**\n{own_file_text}\n\n"
        f"**Existing Policy Document:**\n{existing_file_text}\n\n"
        "Provide a detailed response that directly addresses the question."
    )

    if model == "gemini":
        context = base_query
        result = gemini_llm_api(context)
    
    elif model == "huggingface":

        result = rag_for_huggingface_qa( question, own_file_text, existing_file_text)
    
    elif model == "chatgpt":
        context = base_query
        result = chatgpt_llm_api(context)
    
    else:
        raise ValueError("Unsupported model specified")

    return result



# =================================================================Others files or link sections(Countries Comparative Analysis) =================================================================
# def ComparativeAnalysis(documents_1, documents_2):
#     query = (
#         "Conduct a detailed comparative analysis of the provided documents with a focus on policy alignment. "
#         "Identify and highlight the most important information from each documents"
#         "Provide comparative insights based on these findings, and discuss the implications of the similarities and differences in the context."
#     )
    
#     # Construct a refined context prompt
#     context = (
#         f"Please perform a comparative analysis based on the following query:\n\n"
#         f"Query:\n{query}\n\n"

#         f"Context (Document 1):\n{documents_1}\n\n"
#         f"Context (Document 2):\n{documents_2}\n\n"

#         f"Your analysis should include:\n"
#         f"1. Important information each document.\n"
#         f"2. A comparative evaluation of key points of alignment and divergence.\n"
#         f"3. Insights that discuss the implications of these findings in relation to the broader policy objectives."
#     )
    
#     ComparativeText = gemini_llm_api(context)
#     return ComparativeText

# def extract_article_content(url):
#     go=Goose()
#     content= go.extract(url)
#     return content



# ====================================================== For LLM API Section =================================================================


def text_extraction_process(pdf_file):
    try:
        # Convert InMemoryUploadedFile to a file-like object
        if hasattr(pdf_file, 'read'):
            pdf_file.seek(0)  # Ensure we're at the beginning of the file

        # Read the PDF content
        pdf_reader = PdfReader(pdf_file)
        full_text = ""

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            
            if page_text:
                full_text += page_text
            else:
                # Extract text using OCR as a fallback
                full_text += extract_text_with_ocr(pdf_file, page_num)

        # Ensure the PDF is not empty
        if full_text.strip() == "":
            raise ValueError("The PDF file contains no readable text.")
        
        return full_text

    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")

def extract_text_with_ocr(pdf_file, page_num):
    try:
        # Convert InMemoryUploadedFile to a file-like object for PyMuPDF
        pdf_file.seek(0)  # Ensure we're at the beginning of the file
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        page = pdf_document.load_page(page_num)

        # Convert the page to an image
        pix = page.get_pixmap()
        img = Image.open(BytesIO(pix.tobytes()))

        # Use OCR to extract text from the image
        page_text = pytesseract.image_to_string(img)
        return page_text

    except Exception as e:
        return " "


def suggested_queries(model, text_data):
    # Construct a refined context prompt
    query = (
        "Based on the provided text, generate a list of up to five questions that would help in understanding or analyzing the content. "
        "Return only the questions, without any additional text or headings."
    )
    context = (
        f"**Text:**\n{text_data}\n\n"
        f"**Task:**\n{query}\n\n"
    )

    try:
        if model == "gemini":
            result = gemini_llm_api(context)  # Ensure this is a function call
        elif model == "chatgpt":
            result = chatgpt_llm_api(context)  # Ensure this is a function call
        else:
            return {"error": "Invalid model name provided."}

        # Ensure the result is JSON serializable
        if isinstance(result, dict) or isinstance(result, str):
            return result
        else:
            return {"result": str(result)}  # Convert to string if needed

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


def text_with_query_function(model, text, query):
    # Construct a refined context prompt
    context = (
        f"**Text:**\n{text}\n\n"
        f"**Question:**\n{query}\n\n"
    )

    try:
        if model == "gemini":
            result = gemini_llm_api(context)  # Ensure this is a function call
        elif model == "chatgpt":
            result = chatgpt_llm_api(context)  # Ensure this is a function call
        else:
            return {"error": "Invalid model name provided."}

        # Ensure the result is JSON serializable
        if isinstance(result, dict) or isinstance(result, str):
            return result
        else:
            return {"result": str(result)}  # Convert to string if needed

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    

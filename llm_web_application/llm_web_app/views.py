
# # views.py
# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import OwnUploadedFile , OtherUploadedFile ,ExistingUploadedFile
# import json
# import re
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .utils import process_file , TextSummarization , ComparativeAnalysis  ,suggested_queries , text_with_query_function ,text_extraction_process


# # September 4 , 2024
# # Eror Handling of File and all issues are logged generate a report from the issue tracker

# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import OwnUploadedFile, OtherUploadedFile, ExistingUploadedFile
# import json
# import re
# import logging
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from .utils import process_file, TextSummarization, ComparativeAnalysis

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .utils import (
    process_file, 
    TextSummarization, 
    ComparativeAnalysis, 
    suggested_queries, 
    text_with_query_function, 
    text_extraction_process
)
import json
import re
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def save_upload_file(uploaded_files, folder):
    filename = ""
    absolute_file_path = ""
    for uploaded_file in uploaded_files:
        try:
            # Save the file to the specified directory
            file_path = default_storage.save(f'{folder}/{uploaded_file.name}', ContentFile(uploaded_file.read()))
            absolute_file_path = default_storage.path(file_path)
            filename = uploaded_file.name
        except Exception as e:
            logger.error(f"Error saving file {uploaded_file.name}: {e}")
            return None, None
    return filename, absolute_file_path

@csrf_exempt
def new_policy_file_upload(request):
    if request.method == 'POST':
        try:
            uploaded_files = request.FILES.getlist('files')
            if not uploaded_files:
                return JsonResponse({'status': 'error', 'message': 'No files uploaded.'}, status=400)
            
            filename, absolute_file_path = save_upload_file(uploaded_files, "new_policy_upload_file")
            
            if not absolute_file_path:
                return JsonResponse({'status': 'error', 'message': 'File upload failed.'}, status=500)
            # Store file path in session if needed
            request.session['own_file_path'] = absolute_file_path
            return JsonResponse({'status': 'success', 'filename': filename, 'absolute_file_path': absolute_file_path})

        except Exception as e:
            logger.error(f"Error during own file upload: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing the file.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)




@csrf_exempt
def new_policy_file_summary(request):
    if request.method == 'POST':
        try:
            # Load JSON data from request body
            data = json.loads(request.body.decode('utf-8'))
            filename = data.get('filename')
            absolute_file_path = data.get('absolute_file_path')
            model= data.get('model')

            if not filename or not absolute_file_path:
                return JsonResponse({'status': 'error', 'message': 'Filename or file path missing.'}, status=400)

            # Summarize the uploaded files
            file_texts = process_file(absolute_file_path)  # Ensure this function is defined and works as expected
            summary = TextSummarization(model , file_texts)  # Ensure this function is defined and works as expected

            return JsonResponse({'status': 'success', 'filename': filename, 'summary_of_own_file': summary})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error during file summarization: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing the file.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@csrf_exempt
def existing_policy_file_upload(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.getlist('file')
            if not uploaded_file:
                return JsonResponse({'status': 'error', 'message': 'No files uploaded.'}, status=400)
            
            filename, absolute_file_path = save_upload_file(uploaded_file, "existing_policy_upload_file")
            if not absolute_file_path:
                return JsonResponse({'status': 'error', 'message': 'File upload failed.'}, status=500)
            
            request.session['existing_file_path'] = absolute_file_path

            return JsonResponse({'status': 'success', 'filename': filename, 'message': 'File uploaded successfully.'})

        except Exception as e:
            logger.error(f"Error during existing file upload: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing the file.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def others_file_upload(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.getlist('file')
            if not uploaded_file:
                return JsonResponse({'status': 'error', 'message': 'No files uploaded.'}, status=400)
            
            filename, absolute_file_path = save_upload_file(uploaded_file, "other_upload_file")
            if not absolute_file_path:
                return JsonResponse({'status': 'error', 'message': 'File upload failed.'}, status=500)

            file_texts = process_file(absolute_file_path)
            summary = TextSummarization(file_texts)
            request.session['other_file_path'] = absolute_file_path

            comparative_summary = Comparative_with_others(request)

            return JsonResponse({
                'status': 'success',
                'filename': filename,
                'summary_of_other_file': summary,
                'comparative_summary_of_files': comparative_summary
            })

        except Exception as e:
            logger.error(f"Error during others file upload: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing the file.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def submit_link_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            link = data.get('link', '')
            if not link:
                return JsonResponse({'status': 'error', 'message': 'No link provided.'}, status=400)

            # Parse contents
            contents = extract_article_content(link)
            compare_text = Comparative_with_others_links(request, contents.cleaned_text)
            summary = TextSummarization(contents.cleaned_text)

            return JsonResponse({
                'status': 'success',
                'summary_of_link': summary,
                'comparative_summary_of_files': compare_text
            })

        except Exception as e:
            logger.error(f"Error during link submission: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing the link.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def analyze_document(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            model = data.get('model')
            questions = data.get('questions')

            if not model or not questions:
                return JsonResponse({'status': 'error', 'message': 'Model or questions not provided.'}, status=400)

            question1 = questions.get('question_1')
            question2 = questions.get('question_2')
            question3 = questions.get('question_3')

            own_file_path = request.session.get('own_file_path', None)
            existing_file_path = request.session.get('existing_file_path', None)
            print("Found existing file path")
            print("path 1: ", own_file_path)
            print("path 2: ", existing_file_path)

            if not own_file_path or not existing_file_path:
                return JsonResponse({'status': 'error', 'message': 'File paths missing in session.'}, status=400)

            own_file_text = process_file(own_file_path)
            existing_file_text = process_file(existing_file_path)
            # # Save `own_file_text` to a text file
            # with open("own_file_output.txt", "w" , encoding='utf-8') as own_file:
            #     own_file.write(own_file_text)

            # # Save `existing_file_text` to a text file
            # with open("existing_file_output.txt", "w", encoding='utf-8') as existing_file:
            #     existing_file.write(existing_file_text)

            print("Files have been saved successfully!")

            question_1_result = ComparativeAnalysis(model, question1, own_file_text, existing_file_text)
            question_2_result = ComparativeAnalysis(model, question2, own_file_text, existing_file_text)
            question_3_result = ComparativeAnalysis(model, question3, own_file_text, existing_file_text)

            print("Answer 1::", question_1_result)
            print("\n\n")
            print("Answer 2::", question_2_result)
            print("\n\n")
            print("Answer 3::", question_3_result)
            print("\n\n")

            return JsonResponse({
                'status': 'success',
                'answer_1': question_1_result,
                'answer_2': question_2_result,
                'answer_3': question_3_result
            })

        except Exception as e:
            logger.error(f"Error during document analysis: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred during document analysis.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def Comparative_with_others(request):
    try:
        own_file_path = request.session.get('own_file_path', None)
        others_file_path = request.session.get('other_file_path', None)

        if not own_file_path or not others_file_path:
            raise ValueError('File paths missing in session.')

        own_file_text = process_file(own_file_path)
        others_file_text = process_file(others_file_path)

        compare_text = ComparativeAnalysis(own_file_text, others_file_text)

        return compare_text
    except Exception as e:
        logger.error(f"Error during comparison with others: {e}")
        return "An error occurred during comparison."

def Comparative_with_others_links(request, link_content):
    try:
        own_file_path = request.session.get('own_file_path', None)
        if not own_file_path:
            raise ValueError('File path missing in session.')

        own_file_text = process_file(own_file_path)
        others_file_text = link_content

        compare_text = ComparativeAnalysis(own_file_text, others_file_text)

        return compare_text
    except Exception as e:
        logger.error(f"Error during comparison with link content: {e}")
        return "An error occurred during comparison."


# index renderers
def index(request):
    request.session.pop('own_file_path', None)
    request.session.pop('existing_file_path', None)
    request.session.pop('other_file_path', None)
    return render(request, "index.html")


# For LLM API section 


def summarize(text):
    SummaryText=TextSummarization("gemini" , text)
    return SummaryText



def queries_list(text):
    queries = suggested_queries("gemini", text)
    questions = [q.strip() for q in queries.split('\n') if q.strip()]
    pattern = re.compile(r'^\d+\.\s*')
    cleaned_questions = [pattern.sub('', question).strip() for question in questions]
    
    return cleaned_questions


def continuous_query(text , query):
    answer = text_with_query_function("gemini" , text, query)
    return answer

@csrf_exempt
def pdf_for_summary(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method. Please use POST."}, status=400)
    
    if 'pdf' not in request.FILES:
        return JsonResponse({"error": "No PDF file found in the request."}, status=400)

    try:
        # Get the uploaded PDF file from the request
        pdf_file = request.FILES['pdf']
        
        # Process the PDF file and extract text
        extracted_text = text_extraction_process(pdf_file)
        # print("Extracted Text: " , extracted_text)
        
        # Generate summary from the extracted text
        summary_text = summarize(extracted_text)
        # print("Summary : " , summary_text)
        
        # Define some suggested queries based on the extracted text
        queries =queries_list(summary_text)
        print(queries)
        
        # Return the summary response as JSON
        return JsonResponse({
            "status": "success",
            "extracted_text": extracted_text,
            "summary": summary_text,
            "suggested_queries": queries
        }, status=200)

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


@csrf_exempt
def text_with_query(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method. Please use POST."}, status=400)
    # Parse JSON request body
    data = json.loads(request.body)
    
    if 'text' not in data or 'query' not in data:
        return JsonResponse({"error": "Text and query are required in the request."}, status=400)

    try:
        # Get the text and query from the request
        text = data['text']
        query = data['query']
        
        # Generate text with the given query
        text_with_query_result = continuous_query(text, query)
        
        # Return the response as JSON
        return JsonResponse({"status": "success", "answer": text_with_query_result}, status=200)

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

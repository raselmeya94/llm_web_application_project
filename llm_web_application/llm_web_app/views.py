from django.shortcuts import render


# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .models import OwnUploadedFile , OtherUploadedFile
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .utils import process_file , TextSummarization , ComparativeAnalysis  , extract_article_content

# file upload with drag and drop functionality
# document summarization step here

def save_upload_file(uploaded_files , folder):
    filename = ""
    absolute_file_path= ""
    for uploaded_file in uploaded_files:
        # Save the file to the media/uploads/ directory
        file_path = default_storage.save(f'{folder}/{uploaded_file.name}', ContentFile(uploaded_file.read()))
        # Retrieve the absolute file path
        absolute_file_path = default_storage.path(file_path)
        filename=uploaded_file.name
    return filename, absolute_file_path


own_file_path = ""
@csrf_exempt
def own_file_upload(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('files')
        filename , absolute_file_path =save_upload_file(uploaded_files , "own_upload_file")

        # Summarize the the uploaded files
        FileTexts = process_file(absolute_file_path)
        summary = TextSummarization(FileTexts)
        # print("text:: ", summary)
        request.session['own_file_path'] = absolute_file_path
    
    return JsonResponse({'filename': filename, 'summary_of_own_file': summary})

others_file_path=""
@csrf_exempt
def others_file_upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.getlist('file')
        filename , absolute_file_path =save_upload_file(uploaded_file , "other_upload_file")

        # Summarize the the uploaded files
        FileTexts = process_file(absolute_file_path)
        summary = TextSummarization(FileTexts)

        request.session['other_file_path'] = absolute_file_path
        comparative_summary = Comparative_with_others(request)

    
    return JsonResponse({'filename': filename  , "summary_of_other_file": summary ,  'comparative_summary_of_files': comparative_summary })



def Comparative_with_others(request):
    # first path (own file)
    own_file_path =request.session.get('own_file_path', None)
    # second path (others file)
    others_file_path =  request.session.get('other_file_path', None)

    # Text
    own_file_text = process_file(own_file_path)
    others_file_text = process_file(others_file_path)


    # get the compare
    compare_text = ComparativeAnalysis(own_file_text, others_file_text )

    return compare_text

def Comparative_with_others_links(request , link_content):
    # first path (own file)
    own_file_path =request.session.get('own_file_path', None)
    

    # Text
    own_file_text = process_file(own_file_path)
    others_file_text = link_content


    # get the compare
    compare_text = ComparativeAnalysis(own_file_text, others_file_text )

    return compare_text


@csrf_exempt
def submit_link_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        link = data.get('link', '')
        # Parse contents
        contents= extract_article_content(link)
        compare_text = Comparative_with_others_links(request , contents.cleaned_text)
        summary = TextSummarization(contents.cleaned_text)

        return JsonResponse({'summary_of_link': summary , 'comparative_summary_of_files': compare_text})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)




# index renderers
def index(request):
    return render(request, "index.html")


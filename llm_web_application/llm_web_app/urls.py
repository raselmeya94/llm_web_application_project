

from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('new_policy_file_upload/', views.new_policy_file_upload, name='own-file-upload'),
    path('new_policy_file_summary/', views.new_policy_file_summary, name='new_policy_file_summary'),
    path('other_upload_file/', views.others_file_upload, name='other-file-upload'),
    path('existing_policy_file_upload/', views.existing_policy_file_upload, name='existing_upload_file'),
    path('analyze_document/', views.analyze_document, name='analyze_document'),
    path('submit-link/', views.submit_link_view, name='submit_link'),

    path('api/pdf_to_summary/', views.pdf_for_summary, name='pdf_to_summary'),
    path('api/text_with_query/', views.text_with_query , name='text_with_query')
]
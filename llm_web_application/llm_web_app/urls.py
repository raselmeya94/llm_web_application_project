

from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('own_upload_file/', views.own_file_upload, name='own-file-upload'),
    path('other_upload_file/', views.others_file_upload, name='other-file-upload'),
    # path('submit-link/', views.submit_link_view, name='submit_link'),
    path('submit-link/', views.submit_link_view, name='submit_link'),
]
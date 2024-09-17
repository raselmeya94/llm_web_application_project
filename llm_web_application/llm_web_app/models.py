# models.py
from django.db import models

class OwnUploadedFile(models.Model):
    file = models.FileField(upload_to='new_policy_upload_file/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
class OtherUploadedFile(models.Model):
    file = models.FileField(upload_to='other_upload_file/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ExistingUploadedFile(models.Model):
    file = models.FileField(upload_to='existing_policy_upload_file/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
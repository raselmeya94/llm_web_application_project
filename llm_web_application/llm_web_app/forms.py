# forms.py
from django import forms
from .models import OwnUploadedFile , OtherUploadedFile

class OwnFileUploadForm(forms.ModelForm):
    class Meta:
        model = OwnUploadedFile
        fields = ['file']

class OtherFileUploadForm(forms.ModelForm):
    class Meta:
        model = OtherUploadedFile
        fields = ['file']

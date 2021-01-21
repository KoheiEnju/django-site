from django import forms
from .models import Video


class FileUploadForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ('upload',)
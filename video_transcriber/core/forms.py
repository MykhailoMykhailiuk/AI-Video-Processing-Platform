from django.forms import (
    FileField,
    ModelForm, 
    ClearableFileInput,  
    URLInput, 
    URLField, 
    ValidationError, 
    MultipleChoiceField,
    CheckboxSelectMultiple,
    ChoiceField,
    Select)
from django.core.validators import URLValidator

from .models import Upload, OutputType


class UploadForm(ModelForm):
    file_url = URLField(
        label="Provide the link",
        required=False,
        widget=URLInput(attrs={"class": "form-control"}))
    
    file = FileField(
        label='Browse',
        required=False,
        widget=ClearableFileInput(attrs={'class': 'form-control', 'accept': 'video/*'})
    )
    
    output_types = MultipleChoiceField(
        label="Choose the processing type",
        choices=OutputType.choices,
        widget=CheckboxSelectMultiple
    )

    save_to_file = ChoiceField(
        label="Save to file format",
        choices=[('.txt', 'TXT'), ('.pdf', 'PDF'), ('.docx', 'DOCX')],
        widget=Select(attrs={'class': 'form-select'}),
        required=False,
        initial='.txt'
    )

    class Meta:
        model = Upload
        fields = ['file_url', 'file']

    def clean(self):
        cleaned_data = super().clean()
        file_url = cleaned_data.get('file_url')
        file = cleaned_data.get('file')

        if not file_url and not file:
            raise ValidationError('Please upload a video or provide a URL.')
        
        if file_url and file:
            raise ValidationError('Please upload a video or provide a URL.')
        
        if file_url:
            validator = URLValidator()
            try:
                validator(file_url)
            except ValidationError:
                raise ValidationError("Provide correct video link.")
        
        return cleaned_data
    
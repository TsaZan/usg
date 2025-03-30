from django import forms
from django.utils import timezone
from .models import Content, Category, Tag

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'description', 'content_type', 'platform', 'category', 'tags', 'media_file', 'scheduled_for']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_scheduled_for(self):
        scheduled_for = self.cleaned_data.get('scheduled_for')
        if scheduled_for and scheduled_for < timezone.now():
            raise forms.ValidationError("Scheduled date cannot be in the past.")
        return scheduled_for

    def clean_media_file(self):
        media_file = self.cleaned_data.get('media_file')
        if media_file:
            # Add file size validation (e.g., 10MB limit)
            if media_file.size > 10 * 1024 * 1024:  # 10MB in bytes
                raise forms.ValidationError("File size must not exceed 10MB.")
            
            # Add file type validation
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4']
            if media_file.content_type not in allowed_types:
                raise forms.ValidationError("Invalid file type. Allowed types: JPEG, PNG, GIF, MP4.")
        return media_file

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'parent']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        } 
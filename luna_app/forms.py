# luna_app/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Content
from luna_app.models import UserProfile, Content, Comment

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'location': forms.TextInput(attrs={'placeholder': 'City, Country'}),
        }

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['content_type', 'title', 'description', 'content', 'image', 'location', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a comment...'}),
        }
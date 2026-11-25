from django import forms
from django.contrib.auth.models import User
from .models import Event

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',
        'class': 'form-input'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm your password',
        'class': 'form-input'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'category', 'description', 'date', 'time', 'location', 'capacity', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Event Title', 'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your event...', 'class': 'form-input', 'rows': 4}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'location': forms.TextInput(attrs={'placeholder': 'Event Location (or Online URL)', 'class': 'form-input'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'Maximum attendee capacity', 'class': 'form-input', 'min': 1}),
            'image_url': forms.URLInput(attrs={'placeholder': 'Optional banner image URL', 'class': 'form-input'}),
        }

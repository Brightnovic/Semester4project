from django import forms
from .models import CustomUser , Trainer, Appointment

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(disabled=False)   
    username = forms.CharField(disabled=False)  
    full_name = forms.CharField(required=False)
    
    # Ensure file input is shown properly
    profile_photo = forms.ImageField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'custom-file-input'})  # Ensure file input renders properly
    )

    is_active = forms.BooleanField(disabled=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['profile_photo', 'full_name', 'email', 'username', 'is_active']

 



class UpdateTrainerInfo(forms.ModelForm):
    expertise = forms.CharField(required=False)  # Fix: Changed from `EmailField` to `CharField`

    class Meta:
        model = Trainer
        fields = ['expertise', 'bio', 'instagram_handle', 'facebook_handle', 'linkedin_handle', 'X_handle']



class TrainerAvailabilityForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['available_days', 'max_bookings_per_day']



class ContactForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('Complete_name', 'subject', 'email', 'question_message', 'mobile_number')

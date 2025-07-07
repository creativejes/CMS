from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from .models import Complaint

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


#user profile form 
class UserProfileForm(forms.ModelForm):
    role = forms.ChoiceField(choices=[('student', 'Student'), ('staff', 'Staff')], required=True)
    department = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ['full_name', 'student_id', 'department', 'role', 'avatar']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }



class ComplaintForm(forms.ModelForm):
    confirmation = forms.BooleanField(
        required=True,
        label="I confirm this information is accurate",
        widget=forms.CheckboxInput(attrs={'class': 'mr-2 leading-tight'})
    )

    class Meta:
        model = Complaint
        exclude = ['user', 'status', 'submitted_at', 'updated_at']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'block w-full mt-1 p-2 border border-gray-300 rounded-md',
            }),
            'department': forms.TextInput(attrs={
                'class': 'block w-full mt-1 p-2 border border-gray-300 rounded-md',
                'placeholder': 'Department (optional)'
            }),
            'title': forms.TextInput(attrs={
                'class': 'block w-full mt-1 p-2 border border-gray-300 rounded-md',
                'placeholder': 'Short Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full mt-1 p-2 border border-gray-300 rounded-md',
                'rows': 5,
                'placeholder': 'Enter detailed complaint (300–2000 characters)'
            }),
            'date_of_incident': forms.DateInput(attrs={
                'type': 'date',
                'class': 'block w-full mt-1 p-2 border border-gray-300 rounded-md',
            }),
            'file_attachment': forms.ClearableFileInput(attrs={
                'class': 'block w-full mt-1',
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'mr-2 leading-tight',
            }),
        }

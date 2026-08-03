from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import *
# ============================================
# AUTHENTICATION FORMS
# ============================================

class RegUser(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email',
        ]

# ============================================
# PROFILE FORMS
# ============================================

class StudentForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = StudentProfile
        exclude = ['user']

class MentorForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = MentorProfile
        exclude = ['user']

class CompanyForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = CompanyProfile
        exclude = ['user']

# ============================================
# JOB FORMS
# ============================================

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ['status',"approval_status"]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

# ============================================
# RESUME FORMS
# ============================================

class ResumePersonalForm(forms.ModelForm):
    summary = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Leave blank to generate with AI..."
        })
    )

    class Meta:
        model = ResumePersonal

        fields = [
            'full_name',
            'email',
            'phone',
            'location',
            'linkedin',
            'github',
            'summary'
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "linkedin": forms.URLInput(attrs={"class": "form-control"}),
            "github": forms.URLInput(attrs={"class": "form-control"}),
            "summary": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Write a short professional summary..."
            }),

        }

class ResumeEducationForm(forms.ModelForm):

    class Meta:

        model = ResumeEducation
        fields = [
            "qualification",
            "institution",
            "university",
            "start_year",
            "end_year",
            "cgpa"
        ]

class ResumeProjectForm(forms.ModelForm):

    class Meta:

        model = ResumeProject

        fields = [
            "project_title",
            "technologies",
            "description",
            "github_link",
            "live_link",
        ]

        widgets = {

            "project_title": forms.TextInput(attrs={
                "class":"form-control",
                "placeholder":"CareerAssistant"
            }),

            "technologies": forms.TextInput(attrs={
                "class":"form-control",
                "placeholder":"Python, Django, Bootstrap"
            }),

            "description": forms.Textarea(attrs={
                "class":"form-control",
                "rows":5,
                "placeholder":"Describe your project..."
            }),

            "github_link": forms.URLInput(attrs={
                "class":"form-control"
            }),

            "live_link": forms.URLInput(attrs={
                "class":"form-control"
            }),
        }

class ResumeSkillForm(forms.ModelForm):

    class Meta:

        model = ResumeSkill

        exclude = ["resume"]

        widgets = {

            "technical_skills": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Python, Django, SQL (Optional)"
            }),

            "soft_skills": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Communication, Teamwork"
            }),

            "languages": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "English, Malayalam"
            }),

            "certifications": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "AI-Driven Python Programming - Entri (Optional)"
            }),

        }

class ResumeExperienceForm(forms.ModelForm):

    class Meta:

        model = ResumeExperience

        exclude = ["resume"]

        widgets = {

            "job_title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Python Developer Intern"
            }),

            "company_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. ABC Technologies"
            }),

            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Kochi"
            }),

            "start_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "month"
            }),

            "end_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "month"
            }),

            "currently_working": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe your responsibilities and achievements..."
            }),

        }


class CareerTaskForm(forms.ModelForm):

    class Meta:
        model = CareerTask
        fields = ["title", "category", "priority"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter task title"
            }),

            "category": forms.Select(attrs={
                "class": "form-select"
            }),

            "priority": forms.Select(attrs={
                "class": "form-select"
            }),
        }
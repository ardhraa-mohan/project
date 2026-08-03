from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
# from django.template.loader import get_template
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils import timezone
import random
import re

from .models import *
from .forms import *
from .ai import *

# Import AI functions from existing apps (will need to be moved later)
# try:
from ollama import chat
# except ImportError:
# chat = None

# Import playwright for PDF generation (optional)
# try:
from playwright.sync_api import sync_playwright
# except ImportError:
# sync_playwright = None

# ============================================
# COMMON MODULE VIEWS
# ============================================

def home(request):
    return render(request, 'common/home.html')

def feature(request):
    return render(request, 'common/features.html')

def workpage(request):
    return render(request, 'common/works.html')

def aboutpage(request):
    return render(request, 'common/about.html')

def contactpage(request):
    return render(request, 'common/contact.html')

def privatepage(request):
    return render(request, 'common/base_private.html')

def mentors(request):
    mentors = MentorProfile.objects.all()

    context = {
        "mentors": mentors
    }

    return render(
        request,
        'mentor_module/mentors.html',
        context
    )

# ============================================
# AUTHENTICATION MODULE VIEWS
# ============================================

def student_register(request):
    if request.method == 'POST':
        form = RegUser(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.role = 'student'
            student.save()
            StudentProfile.objects.create(user=student)
            login(request, student)
            return redirect('dashboard')
    else:
        form = RegUser()
    return render(request, 'student_module/authentication/user_register.html', {
    'form': form,
    'title': 'Student Registration',
    'button': 'Register as Student'
})

def mentor_register(request):
    if request.method == 'POST':
        form = RegUser(request.POST)
        if form.is_valid():
            mentor = form.save(commit=False)
            mentor.role = 'mentor'
            mentor.save()
            MentorProfile.objects.create(user=mentor)
            login(request, mentor)
            return redirect('dashboard')
    else:
        form = RegUser()
    return render(request, 'student_module/authentication/user_register.html', {
    'form': form,
    'title': 'Mentor Registration',
    'button': 'Register as Mentor'
})

def company_register(request):
    if request.method == 'POST':
        form = RegUser(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.role = 'company'
            company.save()
            CompanyProfile.objects.create(user=company)
            login(request, company)
            return redirect('dashboard')
        
    else:
        form = RegUser()
    return render(request, 'student_module/authentication/user_register.html', {
    'form': form,
    'title': 'Company Registration',
    'button': 'Register as Company'
})

def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "You have logged in successfully.")
            return redirect('dashboard')
        else:
             messages.error(request, "Invalid username or password.")
    return render(request,'student_module/authentication/login.html')

# def forgot_password(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         try:
#             user = CustomUser.objects.get(email=email)
#             otp = random.randint(100000, 999999)

#             request.session["otp"] = str(otp)
#             request.session["email"] = email

#             send_mail(
#                 "CareerPilot Password Reset OTP",
#                 f"Your OTP is {otp}",
#                 settings.EMAIL_HOST_USER,
#                 [email],
#                 fail_silently=False,
#             )
#             return redirect("verify_otp")
#         except CustomUser.DoesNotExist:
#             messages.error(request, "Email not found.")

#     return render(request, "student_module/authentication/forgot_password.html")

# def verify_otp(request):
#     if request.method == "POST":
#         entered_otp = request.POST.get("otp")
#         if entered_otp == request.session.get("otp"):
#             return redirect("reset_password")
#         else:
#             messages.error(request, "Invalid OTP")

#     return render(request, "student_module/authentication/verify_otp.html")

# def reset_password(request):
#     if request.method == "POST":
#         password = request.POST.get("password")
#         confirm = request.POST.get("confirm_password")

#         if password != confirm:
#             messages.error(request, "Passwords do not match")
#             return redirect("reset_password")

#         email = request.session.get("email")
#         user = CustomUser.objects.get(email=email)
#         user.password = make_password(password)
#         user.save()

#         request.session.flush()
#         messages.success(request, "Password changed successfully.")
#         return redirect("login")

#     return render(request, "student_module/authentication/reset_password.html")

def logoutpage(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect(loginpage)

def registerpage(request):
    return render(request,'student_module/authentication/register.html')

# ============================================
# DASHBOARD MODULE VIEWS
# ============================================

def dashboard(request):
    if request.user.is_superuser:
        return redirect("admin_dashboard")
    elif request.user.role == 'student':
        return redirect('student_dashboard')
    elif request.user.role == 'mentor':
        return redirect('mentor_dashboard')
    elif request.user.role == 'company':
        return redirect('company_dashboard')
    else:
        return redirect('loginpage')

@login_required(login_url='/users/login')
def student_dashboard(request):
    if request.user.role != 'student':
            messages.error(request, "You are not authorized to access the Student Dashboard.")
            return redirect('dashboard')
    else:
        pro = StudentProfile.objects.select_related(
            "mentor",
            "mentor__user"
        ).get(user=request.user)

        mentor = pro.mentor

        profile_incomplete = (
        not pro.phone or
        not pro.location or
        not pro.full_name or
        not pro.course 
        )
        recommended_jobs = Job.objects.all()[:6]

        recent_resumes = (
        Resume.objects.filter(student=pro,is_completed=True).order_by("-created_at")[:5])

        applications = JobApplication.objects.filter(student=pro)

        applied = applications.filter(status="Applied").count()
        shortlisted = applications.filter(status="Shortlisted").count()
        interview = applications.filter(status="Interview").count()
        accepted = applications.filter(status="Selected").count()
        rejected = applications.filter(status="Rejected").count()

        tasks = CareerTask.objects.filter(
            student=request.user
        ).order_by("-created_at")[:3]

        total = CareerTask.objects.filter(
            student=request.user
        ).count()

        completed = CareerTask.objects.filter(
            student=request.user,
            completed=True
        ).count()

        progress = int((completed / total) * 100) if total else 0
        return render(request,'student_module/dashboard/dashboard.html',{
            'pro':pro,
            'profile_incomplete': profile_incomplete,
            'recent_resumes':recent_resumes,
            "applied": applied,
            "pending": shortlisted + interview,
            "accepted": accepted,
            "rejected": rejected,
            'mentor': mentor,
            'recommended_jobs': recommended_jobs,
            "tasks": tasks,
            "progress": progress,
            "completed": completed,
            "total": total,})


# student dashboard mentor feedback
@login_required(login_url="/users/login")
def mentor_feedback(request):

    if request.user.role != "student":
        return redirect("dashboard")

    student = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    mentor = student.mentor

    feedback = None

    if mentor:

        feedback = MentorFeedback.objects.filter(
            mentor=mentor,
            student=student
        ).first()

    context = {
        "mentor": mentor,
        "feedback": feedback,
    }

    return render(
        request,
        "student_module/mentor_feedback.html",
        context
    )

@login_required(login_url="/users/login")
def mentor_dashboard(request):

    if request.user.role != "mentor":
        return redirect("dashboard")

    mentor = get_object_or_404(
        MentorProfile,
        user=request.user
    )

    profile_incomplete = (
        not mentor.full_name or
        not mentor.phone or
        not mentor.qualification or
        not mentor.specialization
    )

    student_count = StudentProfile.objects.filter(
        mentor=mentor
    ).count()

    resume_count = Resume.objects.filter(
        student__mentor=mentor
    ).count()

    interview_count = MockInterview.objects.filter(
        student__mentor=mentor
    ).count()

    context = {
        "mentor": mentor,
        "student_count": student_count,
        "resume_count": resume_count,
        "interview_count": interview_count,
        "profile_incomplete": profile_incomplete,
    }

    return render(
        request,
        "mentor_module/dashboard/mentor_dash.html",
        context
    )

@login_required(login_url='/users/login')
def company_dashboard(request):
    if request.user.role != 'company':
        messages.error(request, "You are not authorized to access the Company Dashboard.")
        return redirect('dashboard')
    else:
        pro = CompanyProfile.objects.get(user=request.user)

        profile_incomplete = (
        not pro.company_name or
        not pro.phone or
        not pro.location
        )

        approved_jobs = Job.objects.filter(
        company=pro,
        approval_status="Approved"
        ).count()

        pending_jobs = Job.objects.filter(
            company=pro,
            approval_status="Pending"
        ).count()

        rejected_jobs = Job.objects.filter(
            company=pro,
            approval_status="Rejected"
        ).count()

        total_applications = JobApplication.objects.filter(
        job__company=pro
        ).count()

        shortlisted = JobApplication.objects.filter(
        job__company=pro,
        status="Shortlisted"
        ).count()

        selected = JobApplication.objects.filter(
        job__company=pro,
        status="Selected"
        ).count()

        pending = JobApplication.objects.filter(
        job__company=pro,
        status="Applied"
        ).count()

        context = {
        'pro': pro,
        'profile_incomplete': profile_incomplete,
        "approved_jobs": approved_jobs,
        "pending_jobs": pending_jobs,
        "rejected_jobs": rejected_jobs,
        'total_applications': total_applications,
        'shortlisted': shortlisted,
        'selected': selected,
        'pending': pending,
        }
        return render(request,'company_module/dashboard/company_dashboard.html',context)

@login_required(login_url='/users/login')
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to access the Company Dashboard.")
        return redirect('dashboard')
    

    context = {
        "total_students": StudentProfile.objects.count(),
        "total_mentors": MentorProfile.objects.count(),
        "total_companies": CompanyProfile.objects.count(),
        "total_jobs": Job.objects.count(),
        "assigned_students" : StudentProfile.objects.filter(mentor__isnull=False).count(),
        "unassigned_students": StudentProfile.objects.filter(mentor__isnull=True).count(),
        "approved_jobs": Job.objects.filter(approval_status="Approved").count(),
        "pending_jobs": Job.objects.filter(approval_status="Pending").count(),
        "rejected_jobs": Job.objects.filter(approval_status="Rejected").count(),
        "recent_users": CustomUser.objects.order_by("-date_joined")[:5],
    }
    
    return render(request,'admin_module/dashboard/admin_dash.html',context)

# ============================================
# STUDENT PROFILE MODULE VIEWS
# ============================================

@login_required(login_url='/users/login')
def student_profile(request):
    if request.user.role != 'student':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard')

    pro = StudentProfile.objects.get(user=request.user)

    return render(request, 'student_module/profile/student_profile.html', {
        'pro': pro
    })
    
@login_required(login_url='/users/login')
def edit_student_profile(request):

    pro = StudentProfile.objects.get(user=request.user)

    if request.method == "POST":

        pro.full_name = request.POST.get("full_name")
        pro.phone = request.POST.get("phone")
        pro.dob = request.POST.get("dob")
        pro.gender = request.POST.get("gender")
        pro.location = request.POST.get("location")
        pro.qualification = request.POST.get("qualification")
        pro.course = request.POST.get("course")
        pro.skills = request.POST.get("skills")
        pro.career_goal = request.POST.get("career_goal")
        pro.occupational_status = request.POST.get("occupational_status")

        if request.FILES.get("profile_pic"):
            pro.profile_pic = request.FILES.get("profile_pic")

        pro.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("student_dashboard")

    return render(request, "student_module/profile/edit_student_profile.html", {
        "pro": pro,"qualification_choices": StudentProfile.QUALIFICATION_CHOICES,"occupational_choices": StudentProfile.OCCUPATIONAL_CHOICES,})

# ============================================
# MENTOR PROFILE MODULE VIEWS
# ============================================

@login_required(login_url='/users/login')
def mentor_profile(request):
    if request.user.role != 'mentor':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard')

    pro = MentorProfile.objects.get(user=request.user)

    return render(request, 'mentor_module/mentor_profile.html', {
        'pro': pro
    })

@login_required(login_url='/users/login')
def edit_mentor_profile(request):

    pro = MentorProfile.objects.get(user=request.user)

    if request.method == "POST":

        pro.full_name = request.POST.get("full_name")
        pro.phone = request.POST.get("phone")
        pro.gender = request.POST.get("gender")
        pro.qualification = request.POST.get("qualification")
        pro.specialization = request.POST.get("specialization")
        pro.experience = request.POST.get("experience")
        pro.company = request.POST.get("company")
        

        if request.FILES.get("profile_pic"):
            pro.profile_pic = request.FILES.get("profile_pic")

        pro.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("mentor_dashboard")

    return render(request, "mentor_module/edit_mentor_profile.html", {
        "pro": pro,"qualification_choices": MentorProfile.QUALIFICATION_CHOICES,
    })

# ============================================
# COMPANY PROFILE MODULE VIEWS
# ============================================

@login_required(login_url='/users/login')
def company_profile(request):
    if request.user.role != 'company':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard')

    pro = CompanyProfile.objects.get(user=request.user)

    return render(request, 'company_module/profile/company_profile.html', {
        'pro': pro
    })

@login_required(login_url='/users/login')
def edit_company_profile(request):
    pro = CompanyProfile.objects.get(user=request.user)

    if request.method == "POST":
        pro.company_name = request.POST.get("company_name")
        pro.industry = request.POST.get("industry")
        pro.phone = request.POST.get("phone")
        pro.location = request.POST.get("location")
        pro.website = request.POST.get("website")
        pro.about = request.POST.get("about")

        pro.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("company_dashboard")

    return render(request, "company_module/profile/edit_company_profile.html", {
        "pro": pro,"industry_choices": CompanyProfile.INDUSTRY_CHOICES,
    })

# ============================================
# COMMUNICATION MODULE VIEWS
# ============================================



def subscription(request):
    return render(request,'student_module/communication/subscription.html')

# def mentornotificationpage(request):
#     return render(request,'mentor_module/communication/mentornotification.html')

def mentorstudentpage(request):
    return render(request,'mentor_module/students/mentorstu.html')

# ============================================
# JOB PORTAL MODULE VIEWS
# ============================================
# company post job
@login_required
def post_job(request):

    if request.method == "POST":

        form = JobForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Job posted successfully!")
            return redirect("my_jobs")
        else:

            messages.error(request, "Job could not be posted. Please check the form.")

    else:
        form = JobForm()

    return render(request, "company_module/jobs/post_job.html", {"form": form})
@login_required
def my_jobs(request):
    jobs = Job.objects.filter(company=request.user.companyprofile)
    return render(request, "company_module/jobs/my_jobs.html", {"jobs": jobs})
@login_required
def manage_jobs(request):
    jobs = Job.objects.filter(company=request.user.companyprofile)
    return render(request, "company_module/jobs/manage_jobs.html", {"jobs": jobs})
@login_required
def view_job(request, id):
    job = get_object_or_404(Job, id=id)
    return render(request, "student_module/job_portal/view_job.html", {"job": job})
@login_required
def edit_job(request, id):

    job = Job.objects.get(id=id)

    if request.method == "POST":

        form = JobForm(request.POST, instance=job)

        if form.is_valid():

            form.save()
            messages.success(request, "Job updated successfully!")

            return redirect("manage_jobs")
        else:
            messages.error(request, "Job could not be updated.")

    else:

        form = JobForm(instance=job)

    return render(request, "company_module/jobs/edit_job.html", {"form": form})

@login_required
def delete_job(request, id):
    job = Job.objects.get(id=id)
    job.delete()
    messages.success(request, "Job deleted successfully!")

    return redirect("manage_jobs")

@login_required
def close_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id,
        company=request.user.companyprofile
    )

    job.status = "Closed"
    job.save()

    return redirect("manage_jobs")

@login_required
def open_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id,
        company=request.user.companyprofile
    )

    job.status = "Open"
    job.save()

    return redirect("manage_jobs")
# -------

# student job portal

def job_portal(request):
    jobs = Job.objects.select_related("company").filter(status="Open",approval_status="Approved").order_by("-posted_on")    
    search = request.GET.get("search")
    location = request.GET.get("location")
    job_type = request.GET.get("job_type")
    sort = request.GET.get("sort")

    if search:
        jobs = jobs.filter(
            Q(job_title__icontains=search) |
            Q(company__company_name__icontains=search)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if sort == "oldest":
        jobs = jobs.order_by("posted_on")
    else:
        jobs = jobs.order_by("-posted_on")

    context = {
        "jobs": jobs,
         "search": search,
        "location": location,
        "job_type": job_type,
        "sort": sort
    }
    
    return render(request, "student_module/job_portal/stu_job_portal.html", context)

def job_details(request, id):
    job = get_object_or_404(Job,id=id,status="Open",approval_status="Approved")
    context = {
        "job": job
    }

    return render(request,"student_module/job_portal/stu_job_details.html",context)

# ============================================
# APPLICATIONS MODULE VIEWS--student
# ============================================

@login_required
def apply_job(request, id):

    if request.user.role != "student":
        messages.error(request, "Only students can apply for jobs.")
        return redirect("dashboard")

    student = StudentProfile.objects.get(user=request.user)
    job = get_object_or_404(Job, id=id)
    resumes = Resume.objects.filter(student=student,is_completed=True).order_by("-created_at")

    # Prevent duplicate applications
    if JobApplication.objects.filter(
    student=student,
    job=job
    ).exists():

        messages.warning(request, "You have already applied for this job.")

        return redirect("job_portal",)

    if request.method == "POST":

        resume = get_object_or_404(Resume,id=request.POST.get("resume"),student=student)
        JobApplication.objects.create(student=student,job=job,resume=resume)

        messages.success(request, "Application submitted successfully.")

        return redirect("job_portal")

    return render(request,"student_module/applications/apply_job.html",
        {
            "job": job,
            "resumes": resumes,
        }
    )

@login_required
def my_applications(request):

    if request.user.role != "student":
        messages.error(request, "Only students can access this page.")
        return redirect("dashboard")

    student = StudentProfile.objects.get(user=request.user)

    applications = JobApplication.objects.filter(
        student=student
    ).order_by("-applied_at")

    return render(
        request,
        "student_module/applications/my_applications.html",
        {
            "applications": applications
        }
    )

# ============================================
# RECRUITMENT MODULE VIEWS
# ============================================

@login_required
def company_applicants(request):

    company = CompanyProfile.objects.get(
        user=request.user
    )

    jobs = Job.objects.filter(
        company=company
    ).order_by("-id")

    context = {
        "jobs": jobs,
    }

    return render(
        request,
        "company_module/recruitment/company_applicants.html",
        context,
    )

@login_required
def view_applicants(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    applications = JobApplication.objects.filter(
        job=job
    ).select_related(
        "student",
        "resume"
    )

    context = {

        "job": job,

        "applications": applications,

    }

    return render(
        request,
        "company_module/recruitment/view_applicants.html",
        context,
    )

@login_required
def company_resume_view(request, application_id):

    application = get_object_or_404(
        JobApplication,
        id=application_id
    )

    resume = application.resume

    context = get_resume_data(resume)

    # Add these lines
    context["resume"] = resume
    context["application"] = application
    context["job"] = application.job

    if resume.template == "professional":
        template = "student_module/resume_builder/resume/professional_resume.html"

    elif resume.template == "modern":
        template = "student_module/resume_builder/resume/modern_resume.html"

    else:
        template = "student_module/resume_builder/resume/minimal_resume.html"

    return render(request, template, context)

@login_required
def view_application(request, id):

    application = get_object_or_404(
        JobApplication,
        id=id
    )
    

    if request.method == "POST":

        application.status = request.POST.get("status")
        application.save()

        messages.success(
            request,
            "Application status updated successfully."
        )

        return redirect(
            "view_application",
            id=id
        )

    return render(
        request,
        "company_module/recruitment/view_application.html",
        {
            "application": application
            
        }
    )

@login_required
def shortlisted_candidates(request):

    company = CompanyProfile.objects.get(user=request.user)

    applications = JobApplication.objects.filter(
        job__company=company,
        status="Shortlisted"
    ).select_related("student", "job").order_by("-applied_at")

    context = {
        "applications": applications,
    }

    return render(
        request,
        "company_module/recruitment/shortlisted_candidates.html",
        context,
    )

# ============================================
# RESUME BUILDER MODULE VIEWS
# ============================================
@login_required
def resume_dashboard(request):
    return render(request, "student_module/resume_builder/resume_dashboard.html")

@login_required
def resume_feedback(request):

    student = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    resumes = Resume.objects.filter(
        student=student
    ).order_by("-feedback_date")

    return render(
        request,
        "student_module/resume_builder/resume_feedback.html",
        {
            "resumes": resumes
        }
    )

@login_required
def feedback_view_resume(request, resume_id):

    student = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    resume = get_object_or_404(
        Resume,
        id=resume_id,
        student=student
    )

    if resume.template == "professional":
        template_name = "student_module/resume_builder/resume/professional_resume_feedback.html"

    elif resume.template == "modern":
        template_name = "student_module/resume_builder/resume/modern_resume_feedback.html"

    else:
        template_name = "student_module/resume_builder/resume/minimal_resume_feedback.html"

    context = get_resume_data(resume)
    context["resume"] = resume

    return render(
        request,
        template_name,
        context
    )

@login_required
def resume_builder(request):

    jobs = Job.objects.select_related("company").all()

    if request.method == "POST":

        student = get_object_or_404(
            StudentProfile,
            user=request.user
        )

        job = get_object_or_404(
            Job,
            id=request.POST.get("job")
        )

        resume = Resume.objects.create(
            student=student,
            resume_name=request.POST.get("resume_name"),
            target_job=job,
            template=request.POST.get("template")
        )


        return redirect(
            "resume_personal_details",
            resume.id
        )

    return render(
        request,
        "student_module/resume_builder/resume_builder.html",
        {
            "jobs": jobs
        }
    )

@login_required
def resume_personal_details(request, id):
    resume = get_object_or_404(Resume, id=id)
    student = StudentProfile.objects.get(user=request.user)
    if request.method == "POST":
        form = ResumePersonalForm(request.POST)
        if form.is_valid():
            personal = form.save(commit=False)
            personal.resume = resume
            personal.save()
            return redirect("resume_education", resume.id)

    else:

        form = ResumePersonalForm(initial={

            "full_name": student.full_name,
            "email": student.user.email,
            "phone": student.phone,
            "location": student.location,

        })
    return render(request,"student_module/resume_builder/resume_personal_details.html",{"form": form,"resume": resume})

@login_required
def resume_education(request, id):

    resume = get_object_or_404(Resume, id=id)

    if request.method == "POST":

        form = ResumeEducationForm(request.POST)

        if form.is_valid():

            education = form.save(commit=False)
            education.resume = resume
            education.save()

            return redirect("resume_education", resume.id)

    else:
        form = ResumeEducationForm()

    educations = ResumeEducation.objects.filter(resume=resume)

    return render(
        request,
        "student_module/resume_builder/resume_education.html",
        {
            "form": form,
            "resume": resume,
            "educations": educations
        }
    )

@login_required
def edit_education(request, id):

    education = get_object_or_404(ResumeEducation, id=id)

    if request.method == "POST":

        form = ResumeEducationForm(request.POST, instance=education)

        if form.is_valid():

            form.save()

            return redirect("resume_education", education.resume.id)

    else:

        form = ResumeEducationForm(instance=education)

    return render(request, "student_module/resume_builder/resume_education.html", {
        "form": form,
        "resume": education.resume,
        "educations": ResumeEducation.objects.filter(resume=education.resume),      #This gets all education records belonging to the same resume.
    })

@login_required
def delete_education(request, id):

    education = get_object_or_404(ResumeEducation, id=id)

    resume_id = education.resume.id

    education.delete()

    return redirect("resume_education", resume_id)

@login_required
def resume_projects(request, id):

    resume = get_object_or_404(Resume, id=id)

    if request.method == "POST":

        form = ResumeProjectForm(request.POST)

        if form.is_valid():

            project = form.save(commit=False)
            project.resume = resume
            project.save()

            return redirect("resume_projects", resume.id)

    else:
        form = ResumeProjectForm()

    projects = ResumeProject.objects.filter(resume=resume)

    context = {
        "form": form,
        "resume": resume,
        "projects": projects,
    }

    return render(request, "student_module/resume_builder/resume_projects.html", context)

@login_required
def edit_project(request, id):

    project = get_object_or_404(ResumeProject, id=id)

    if request.method == "POST":

        form = ResumeProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return redirect("resume_projects", project.resume.id)

    else:
        form = ResumeProjectForm(instance=project)

    projects = ResumeProject.objects.filter(resume=project.resume)

    return render(
        request,
        "student_module/resume_builder/resume_projects.html",
        {
            "form": form,
            "resume": project.resume,
            "projects": projects,
        },
    )

@login_required
def delete_project(request, id):

    project = get_object_or_404(ResumeProject, id=id)

    resume_id = project.resume.id

    project.delete()

    return redirect("resume_projects", resume_id)

@login_required
def resume_skills(request, id):

    resume = get_object_or_404(Resume, id=id)

    # Get existing skills or create an empty record
    skill, created = ResumeSkill.objects.get_or_create(resume=resume)

    if request.method == "POST":

        form = ResumeSkillForm(request.POST, instance=skill)

        if form.is_valid():

            form.save()

            return redirect("resume_skills", resume.id)

    else:

        form = ResumeSkillForm(instance=skill)

    return render(
        request,
        "student_module/resume_builder/resume_skills.html",
        {
            "form": form,
            "resume": resume,
            "skills": skill,
        },
    )

@login_required
def resume_experience(request, id):

    resume = get_object_or_404(Resume, id=id)

    if request.method == "POST":

        form = ResumeExperienceForm(request.POST)

        if form.is_valid():

            experience = form.save(commit=False)
            experience.resume = resume
            experience.save()

            return redirect("resume_experience", resume.id)

    else:

        form = ResumeExperienceForm()

    experiences = ResumeExperience.objects.filter(resume=resume)

    return render(
        request,
        "student_module/resume_builder/resume_experience.html",
        {
            "form": form,
            "resume": resume,
            "experiences": experiences,
        }
    )

@login_required
def edit_experience(request, id):

    experience = get_object_or_404(ResumeExperience, id=id)

    if request.method == "POST":

        form = ResumeExperienceForm(
            request.POST,
            instance=experience
        )

        if form.is_valid():

            form.save()

            return redirect(
                "resume_experience",
                experience.resume.id
            )

    else:

        form = ResumeExperienceForm(
            instance=experience
        )

    experiences = ResumeExperience.objects.filter(
        resume=experience.resume
    )

    return render(
        request,
        "student_module/resume_builder/resume_experience.html",
        {
            "form": form,
            "resume": experience.resume,
            "experiences": experiences,
        }
    )

@login_required
def delete_experience(request, id):

    experience = get_object_or_404(
        ResumeExperience,
        id=id
    )

    resume_id = experience.resume.id

    experience.delete()

    return redirect(
        "resume_experience",
        resume_id
    )

def ask_ai(prompt):

    try:

        response = chat(
            model="llama3.1:8b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.message.content.strip()

    except Exception:

        return ""

def get_resume_data(resume):

    personal = ResumePersonal.objects.filter(resume=resume).first()
    educations = ResumeEducation.objects.filter(resume=resume)
    projects = ResumeProject.objects.filter(resume=resume)
    skills = ResumeSkill.objects.filter(resume=resume).first()
    experiences = ResumeExperience.objects.filter(resume=resume)

    education_text = "\n".join(
        f"""
Qualification : {edu.qualification}
Institution : {edu.institution}
University : {edu.university}
Duration : {edu.start_year} - {edu.end_year}
CGPA : {edu.cgpa}
"""
        for edu in educations
    )

    project_text = "\n".join(
        f"""
Project : {project.project_title}
Technologies : {project.technologies}
Description : {project.description}
"""
        for project in projects
    )

    if experiences.exists():

        experience_text = "\n".join(
            f"""
Job Title : {exp.job_title}
Company : {exp.company_name}
Location : {exp.location}
Duration : {exp.start_date} - {"Present" if exp.currently_working else exp.end_date}
Description : {exp.description}
"""
            for exp in experiences
        )

    else:

        experience_text = "Candidate is a fresher with no work experience."

    # ---------------- Summary ----------------

    ai_summary = personal.summary if personal and personal.summary else ""

    if personal and not personal.summary:

        ai_summary = ask_ai(f"""
You are a professional ATS resume writer.

Candidate Name:
{personal.full_name}

Target Job:
{resume.target_job.job_title}

Education:
{education_text}

Projects:
{project_text}

Experience:
{experience_text}

Write a professional ATS friendly summary.
Maximum 80 words.
Write in third person or implied first person without using "I".
Do NOT include headings.
Do NOT include quotation marks.
Do NOT write "Here's the summary".
Do NOT write explanations or notes.
Do NOT mention the word "summary".
Return ONLY the final resume summary text.
""")

    # ---------------- Technical Skills ----------------

    ai_technical_skills = ""

    if skills:

        if skills.technical_skills:

            ai_technical_skills = skills.technical_skills

        else:

            ai_technical_skills = ask_ai(f"""
You are writing an ATS resume.

Target Job:
{resume.target_job.job_title}

Return ONLY a comma-separated list.

Example:
Python, Django, SQL, Git, HTML, CSS, JavaScript

Do not write any sentence.
Do not explain anything.
Do not use bullets.
""")

    # ---------------- Soft Skills ----------------

    ai_soft_skills = ""

    if skills:

        if skills.soft_skills:

            ai_soft_skills = skills.soft_skills

        else:

            ai_soft_skills = ask_ai(f"""
You are writing an ATS resume.

Target Job:
{resume.target_job.job_title}

Return ONLY a comma-separated list.

Example:
Communication, Teamwork, Problem Solving, Leadership, Time Management

Do not explain.
Do not write sentences.
Do not use bullets.
""")

    # ---------------- Projects ----------------

    ai_projects = []

    

    for project in projects:

        description = project.description

        if project.description:

            description = ask_ai(f"""
You are an ATS resume writer.

Rewrite ONLY the project description.

Project Title:
{project.project_title}

Technologies:
{project.technologies}

Original Description:
{project.description}

Rules:

- Maximum 60 words.
- Professional tone.
- ATS friendly.
- Improve grammar.
- Do NOT invent new features.
- Do NOT add headings.
- Do NOT write explanations.
- Do NOT say "Here is the rewritten version".
- Return ONLY the final project description.

Output example:

""")

        ai_projects.append({
        "title": project.project_title,
        "technologies": project.technologies,
        "description": description,
        "github_link": project.github_link,
        "live_link": project.live_link,
    })

    return {
        "personal": personal,
        "educations": educations,
        "projects": projects,
        "skills": skills,
        "experiences": experiences,
        "ai_summary": ai_summary,
        "ai_technical_skills": ai_technical_skills,
        "ai_soft_skills": ai_soft_skills,
        "ai_projects": ai_projects,
    }

@login_required
def resume_preview(request, id):

    resume = get_object_or_404(Resume, id=id)

    if resume.template == "professional":
        template_name = "student_module/resume_builder/resume/professional_resume.html"

    elif resume.template == "modern":
        template_name = "student_module/resume_builder/resume/modern_resume.html"

    elif resume.template == "minimal":
        template_name = "student_module/resume_builder/resume/minimal_resume.html"

    context = get_resume_data(resume)

    context["resume"] =  resume

    return render(request, template_name, context)

@login_required
def resume_preview_apply(request, resume_id, job_id):

    resume = get_object_or_404(Resume, id=resume_id)

    if resume.template == "professional":
        template_name = "student_module/resume_builder/resume/professional_resume.html"
    elif resume.template == "modern":
        template_name = "student_module/resume_builder/resume/modern_resume.html"
    elif resume.template == "minimal":
        template_name = "student_module/resume_builder/resume/minimal_resume.html"

    context = get_resume_data(resume)

    context["resume"] = resume      
    context["job_id"] = job_id     
    context["from_apply"] = True

    return render(request, template_name, context)

@login_required
def resume_pdf(request, id):

    if sync_playwright is None:
        messages.error(request, "PDF generation not available. Playwright is not installed.")
        return redirect("student_dashboard")

    resume = get_object_or_404(Resume, id=id)

    if resume.template == "professional":
        template_name = "student_module/resume_builder/resume/professional_resume.html"

    elif resume.template == "modern":
        template_name = "student_module/resume_builder/resume/modern_resume.html"

    elif resume.template == "minimal":
        template_name = "student_module/resume_builder/resume/minimal_resume.html"

    context = get_resume_data(resume)
    context["resume"] = resume

    html = render_to_string(template_name, context)

    with sync_playwright() as p:

        browser = p.chromium.launch()

        page = browser.new_page()

        page.set_content(html)

        pdf_bytes = page.pdf(format="A4")

        browser.close()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")

    response["Content-Disposition"] = f'attachment; filename="{resume.resume_name}.pdf"'

    return response


@login_required
def finish_resume(request, id):

    resume = get_object_or_404(
        Resume,
        id=id
    )

    resume.is_completed = True
    resume.save()


    messages.success(
        request,
        "Resume created successfully."
    )

    return redirect("student_dashboard")


@login_required
def delete_resume(request, id):
    resume = get_object_or_404(Resume, id=id)
    if request.method == "POST":
        resume.delete()
        messages.success(request, "Resume deleted successfully.")
        return redirect("student_dashboard")
    return render(request, 'student_module/resume_builder/delete_resume.html', {'resume': resume})

# ============================================
# CAREER GUIDANCE MODULE VIEWS
# ============================================

@login_required
def career_assessment(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    
    # CHECK COMPLETED ACTIVE ASSESSMENT
    

    completed = CareerConversation.objects.filter(
        student=student,
        completed=True,
        is_active=True
    ).order_by("-started_at").first()



    if completed:

        report = CareerReport.objects.filter(
            conversation=completed
        ).first()


        current_career = StudentCareer.objects.filter(
            student=student,
            active=True
        ).first()



        return render(
            request,
            "student_module/career_guidance/career/assessment_dashboard.html",
            {
                "report": report,

                "current_career": current_career,

                "recommended": report.recommended_careers
                if report else [],

                "completed_date": completed.completed_at
            }
        )



    
    # CREATE / GET ACTIVE CHAT
    

    conversation, created = CareerConversation.objects.get_or_create(

        student=student,

        completed=False,

        is_active=True

    )



    answers = CareerMessage.objects.filter(

        conversation=conversation,

        sender="student"

    ).order_by("created_at")



    current_index = answers.count()



  
    # FIRST QUESTION
    

    if created:

        CareerMessage.objects.create(

            conversation=conversation,

            sender="assistant",

            message=CAREER_QUESTIONS[0]

        )




    #
    # FINISHED ASSESSMENT
    

    if current_index >= len(CAREER_QUESTIONS):


        conversation.completed = True

        conversation.completed_at = timezone.now()

        conversation.save()




        return redirect(

            "generate_career_report",

            conversation.id

        )




    # ==================================
    # SAVE STUDENT ANSWER
    # ==================================

    if request.method == "POST":


        answer = request.POST.get(
            "message"
        )


        if answer:


            CareerMessage.objects.create(

                conversation=conversation,

                sender="student",

                message=answer

            )



            next_index = current_index + 1




            if next_index < len(CAREER_QUESTIONS):


                CareerMessage.objects.create(

                    conversation=conversation,

                    sender="assistant",

                    message=CAREER_QUESTIONS[next_index]

                )



        return redirect(
            "career_assessment"
        )




    # ==================================
    # LOAD CHAT
    # ==================================

    messages = CareerMessage.objects.filter(

        conversation=conversation

    ).order_by("created_at")




    return render(

        request,

        "student_module/career_guidance/career/assessment.html",

        {

            "conversation": conversation,

            "chat_messages": messages,

        }

    )

import re

@login_required 
def generate_career_report(request, id): 
    conversation = get_object_or_404( CareerConversation, id=id ) 
    # Check existing report 
    report = CareerReport.objects.filter( conversation=conversation ).first() 
    if report: 
        return redirect( "career_report", conversation.id ) 
    # Student answers 
    answers = CareerMessage.objects.filter( conversation=conversation, sender="student" ).order_by("created_at") 
    # Generate AI report

    report_text = generate_report( list(answers) ) 

    # Recommended careers 
    # Temporary data
    # Later replace with AI extracted careers 

    # recommended = [ 
    #     { "name": "Python Developer", "confidence": 90 },
    #     { "name": "Data Analyst", "confidence": 80 },
    #     { "name": "Machine Learning Engineer", "confidence": 75 } ]
    recommended = []

    pattern = r"Career:\s*(.*?)\s*Confidence:\s*(\d+)"

    matches = re.findall(pattern, report_text)
    # print("REPORT:")
    # print(report_text)

    # print("MATCHES:")
    # print(matches)

    for career, confidence in matches:

        recommended.append({
            "name": career.strip(),
            "confidence": int(confidence)
        })
    # Save report 
    CareerReport.objects.create( conversation=conversation, report=report_text, recommended_careers=recommended )
    # Complete assessment 
    conversation.completed = True 
    conversation.save() 
    return redirect( "career_report", conversation.id )

@login_required
def career_report(request, id):

    conversation = get_object_or_404(
        CareerConversation,
        id=id
    )


    report = get_object_or_404(
        CareerReport,
        conversation=conversation
    )


    context = {

        "conversation": conversation,

        "report": report,

    }


    return render(
        request,
        "student_module/career_guidance/career/career_report.html",
        context
    )

@login_required
def select_career(request, career_name):

    student = StudentProfile.objects.get(
        user=request.user
    )


    # Remove old active career

    StudentCareer.objects.filter(
        student=student,
        active=True
    ).update(
        active=False
    )



    # Activate / Create selected career

    career, created = StudentCareer.objects.get_or_create(

        student=student,

        career_name=career_name,

        defaults={
            "confidence":0,
            "active":True
        }

    )


    if not created:

        career.active = True
        career.selected_at = timezone.now()
        career.save()



    return redirect(
        "career_assessment"
    )

@login_required
def change_career(request):

    student = StudentProfile.objects.get(
        user=request.user
    )


    current_career = StudentCareer.objects.filter(
        student=student,
        active=True
    ).first()


    return render(
        request,
        "student_module/career_guidance/career/change_career.html",
        {
            "current_career": current_career
        }
    )

@login_required
def confirm_change_career(request):

    student = StudentProfile.objects.get(
        user=request.user
    )


    StudentCareer.objects.filter(
        student=student,
        active=True
    ).update(
        active=False
    )


    return redirect(
        "career_assessment"
    )

@login_required
def retake_assessment(request):

    student = StudentProfile.objects.get(
        user=request.user
    )


    # Archive previous assessment

    CareerConversation.objects.filter(
        student=student,
        is_active=True,
        completed=True
    ).update(
        is_active=False
    )



    # Remove current selected career

    StudentCareer.objects.filter(
        student=student,
        active=True
    ).update(
        active=False
    )



    # Create new conversation

    conversation = CareerConversation.objects.create(
        student=student,
        completed=False,
        is_active=True
    )



    # Add first AI question

    CareerMessage.objects.create(
        conversation=conversation,
        sender="assistant",
        message=CAREER_QUESTIONS[0]
    )



    return redirect(
        "career_assessment"
    )

# ============================================
# CAREER ROADMAP MODULE VIEWS
# ============================================

@login_required
def roadmap(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    career = StudentCareer.objects.filter(
        student=student,
        active=True
    ).first()

    if career is None:

        return render(request,
            "student_module/career_roadmap/careerroadmap/no_career.html"
        )

    roadmap = CareerRoadmap.objects.filter(
        student=student,
        career=career
    ).first()

    if roadmap is None:

        ai_report = generate_roadmap(
            student,
            career
        )

        roadmap = CareerRoadmap.objects.create(
            student=student,
            career=career,
            roadmap=ai_report
        )

    return render(
        request,
        "student_module/career_roadmap/careerroadmap/roadmap.html",
        {
            "career": career,
            "roadmap": roadmap
        }
    )

# ============================================
# SKILL GAP MODULE VIEWS
# ============================================

@login_required
def skill_gap(request):

    student = StudentProfile.objects.get(user=request.user)
    career = StudentCareer.objects.filter(
        student=student,
        active=True
    ).first()
    if career is None:
        messages.warning(request, "Please select a career first.")
        return redirect("career_assessment")

    report = SkillGap.objects.filter(
        student=student,
        career=career
    ).first()

    if report is None:

        report = SkillGap.objects.create(

            student=student,

            career=career,

            report=generate_skill_gap(
                student,
                career
            )

        )

    return render(request,"student_module/skill_gap/skillgap/skill_gap.html",
        {
            "career":career,
            "report":report
        }

    )

# ============================================
# MOCK INTERVIEW MODULE VIEWS
# ============================================

@login_required
def mock_interview(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    career = StudentCareer.objects.filter(
        student=student,
        active=True
    ).first()

    context = {

        "career": career

    }

    return render(
        request,
        "student_module/mock_interview/mockinterview/mock_interview.html",
        context
    )

@login_required
def start_mock_interview(request):

    if request.method == "POST":

        student = StudentProfile.objects.get(
            user=request.user
        )

        career = StudentCareer.objects.get(
            student=student,
            active=True
        )

        difficulty = request.POST.get("difficulty")

        total = int(
            request.POST.get("questions")
        )

        interview = MockInterview.objects.create(

            student=student,

            career=career,

            difficulty=difficulty,

            total_questions=total

        )

        questions = generate_questions(
            career.career_name,
            difficulty,
            total
        )

        # Remove any existing "Tell me about yourself?" question
        questions = [
            q for q in questions
            if q.lower().strip() != "tell me about yourself?"
        ]

        # Insert it as the first question
        questions.insert(0, "Tell me about yourself?")
        questions = questions[:total]

        order = 1

        for q in questions:

            q = q.strip()

            if q == "":
                continue

            InterviewQuestion.objects.create(

                interview=interview,

                question=q,

                order=order

            )

            order += 1

        first_question = interview.questions.order_by("order").first()

        return redirect(

            "interview_question",

            first_question.id

        )

    return redirect("mock_interview")

@login_required
def interview_question(request, pk):

    question = get_object_or_404(
        InterviewQuestion,
        id=pk
    )

    if request.method == "POST":

        question.answer = request.POST.get("answer")
        question.save()

        next_question = InterviewQuestion.objects.filter(

            interview=question.interview,

            order=question.order + 1

        ).first()

        if next_question:

            return redirect(

                "interview_question",

                next_question.id

            )

        interview = question.interview

        interview.completed = True

        report = evaluate_interview(

            interview.career.career_name,

            interview.questions.all()

        )

        interview.ai_report = report

        # Extract scores

        def extract_score(text, label):

            text = text.replace("**", "")
            pattern = rf"{re.escape(label)}\s*:\s*(\d+)"

            match = re.search(pattern, text, re.IGNORECASE)

            if match:

                return int(match.group(1))

            return 0

        interview.overall_score = extract_score(
            report,
            "Overall Score"
        )

        interview.technical_score = extract_score(
            report,
            "Technical Score"
        )

        interview.communication_score = extract_score(
            report,
            "Communication Score"
        )

        interview.confidence_score = extract_score(
            report,
            "Confidence Score"
        )

        interview.save()

        return redirect(
            "interview_report",
            interview.id
        )

    total = question.interview.total_questions

    progress = int(

        (question.order / total) * 100

    )

    context = {

        "question": question,

        "progress": progress

    }

    return render(

        request,

        "student_module/mock_interview/mockinterview/interview_question.html",

        context

    )

@login_required
def interview_report(request, pk):

    interview = get_object_or_404(

        MockInterview,

        id=pk

    )

    context = {

        "interview": interview,

        "questions": interview.questions.all()

    }

    return render(

        request,

        "student_module/mock_interview/mockinterview/interview_report.html",

        context

    )


@login_required
def interview_history(request):

    student = StudentProfile.objects.get(
        user=request.user
    )

    interviews = MockInterview.objects.filter(
        student=student,
        completed=True
    ).order_by("-created_at")

    context = {
        "interviews": interviews
    }

    return render(
        request,
        "student_module/mock_interview/mockinterview/interview_history.html",
        context
    )



@login_required
def student_interview_feedback(request):

    student = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    interviews = MockInterview.objects.filter(
        student=student
    ).order_by("-feedback_date")

    return render(
        request,
        "student_module/mock_interview/student_interview_feedback.html",
        {
            "interviews": interviews
        }
    )

# ============================================
# CHAT MODULE VIEWS
# ============================================

@login_required
def my_mentor(request):

    student = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    if student.mentor is None:

        return render(
            request,
            "student_module/doubt/no_mentor.html"
        )

    room, created = ChatRoom.objects.get_or_create(

        student=student,

        defaults={
            "mentor": student.mentor
        }

    )

    if request.method == "POST":

        text = request.POST.get("message")

        if text:

            Message.objects.create(

                room=room,

                sender=request.user,

                text=text

            )

        return redirect("my_mentor")

    chat_messages = room.messages.all()

    context = {

        "mentor": student.mentor,

        "room": room,

        "chat_messages": chat_messages,

    }

    return render(

        request,

        "student_module/doubt/my_mentor.html",

        context

    )

# ==============
# mentor chat
# =================

@login_required
def mentor_chat_list(request):

    if request.user.role != "mentor":
        return redirect("dashboard")

    mentor = get_object_or_404(
        MentorProfile,
        user=request.user
    )

    search = request.GET.get("search", "")

    rooms = ChatRoom.objects.filter(
        mentor=mentor
    ).select_related(
        "student",
        "student__user"
    )

    if search:

        rooms = rooms.filter(

            Q(student__full_name__icontains=search) |
            Q(student__full_name__istartswith=search) |
            Q(student__user__username__icontains=search)

        )
    # Add last message and unread count for each room
    for room in rooms:

        room.last = room.messages.last()

        room.unread = room.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).count()


    return render(
        request,
        "mentor_module/chat/chat_list.html",
        {
            "rooms": rooms,
            "search": search
        }
    )

@login_required
def mentor_chat(request, room_id):

    if request.user.role != "mentor":
        return redirect("dashboard")

    mentor = get_object_or_404(
        MentorProfile,
        user=request.user
    )

    room = get_object_or_404(
        ChatRoom,
        id=room_id,
        mentor=mentor
    )

    room.messages.filter(

        is_read=False

    ).exclude(

        sender=request.user

    ).update(

        is_read=True

    )

    if request.method == "POST":

        text = request.POST.get("message")

        if text:

            Message.objects.create(

                room=room,

                sender=request.user,

                text=text

            )

        return redirect(
            "mentor_chat",
            room.id
        )

    return render(
        request,
        "mentor_module/chat/chat.html",
        {
            "room": room,
            "student": room.student,
            "chat_messages": room.messages.all()
        } 
    )

# ============================================
# ADMIN PANEL MODULE VIEWS
# ============================================

@login_required(login_url='/users/login')
def manage_students(request):

    if not request.user.is_superuser:
        return redirect('dashboard')

    students = StudentProfile.objects.select_related('user')
    search = request.GET.get('search')

    if search:
        students = students.filter(
            Q(user__username__icontains=search) |
            Q(name__istartswith=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )
    for student in students:
        student.current_career = StudentCareer.objects.filter(
            student=student,
            active=True
        ).first()

    return render(request,'admin_module/manage_students/manage_students.html',{'students': students})

@login_required(login_url='/users/login')
def student_detail(request, id):

    if not request.user.is_superuser:
        return redirect('dashboard')

    student = get_object_or_404(StudentProfile.objects.select_related('user'),id=id)
    current_career = StudentCareer.objects.filter(student=student,active=True).first()
    resume = Resume.objects.filter(student=student).first()
    report = CareerReport.objects.filter(conversation__student=student).order_by('-created_at').first()    
    roadmap = CareerRoadmap.objects.filter(student=student).first()
    skillgap = SkillGap.objects.filter(student=student).first()
    interview = MockInterview.objects.filter(student=student).order_by('-created_at').first()

    applications = JobApplication.objects.filter(student=student)

    context = {
        "student": student,
        "career": current_career,
        "resume": resume,
        "report": report,
        "roadmap": roadmap,
        "skillgap": skillgap,
        "interview": interview,
        "total_applications": applications.count(),
        "accepted": applications.filter(status="Accepted").count(),
        "rejected": applications.filter(status="Rejected").count(),
        "pending": applications.filter(status="Pending").count(),
    }

    return render(
        request,
        "admin_module/manage_students/student_details.html",
        context
    )

@login_required(login_url='/users/login')
def delete_student(request, id):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized.")
        return redirect("dashboard")

    student = get_object_or_404(StudentProfile, id=id)

    if request.method == "POST":
        user = student.user
        user.delete()   
        messages.success(request, "Student deleted successfully.")
        return redirect("manage_students")

    return render(request, "admin_module/manage_students/delete_student.html", {
        "student": student
    })

@login_required(login_url='/users/login')
def manage_mentors(request):

    if not request.user.is_superuser:
        return redirect('dashboard')
    
    mentors = MentorProfile.objects.select_related('user')

    search = request.GET.get('search')

    if search:
        mentors = mentors.filter(
            Q(user__username__icontains=search) |
            Q(name__istartswith=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )

    return render(request,'admin_module/manage_mentors/manage_mentors.html',{'mentors': mentors})

@login_required(login_url='/users/login')
def mentor_detail(request, id):

    if not request.user.is_superuser:
        return redirect('dashboard')

    mentor = get_object_or_404(
        MentorProfile.objects.select_related('user'),
        id=id
    )

    context = {
        "mentor": mentor,
    }

    return render(request,"admin_module/manage_mentors/mentor_details.html",context)

@login_required(login_url='/users/login')
def delete_mentor(request, id):

    if not request.user.is_superuser:
        messages.error(request, "You are not authorized.")
        return redirect("dashboard")

    mentor = get_object_or_404(MentorProfile, id=id)

    if request.method == "POST":
        user = mentor.user
        user.delete()
        messages.success(request, "Mentor deleted successfully.")
        return redirect("manage_mentors")

    return render(request, "admin_module/manage_mentors/delete_mentor.html", {"mentor": mentor})

@login_required(login_url="/users/login")
def manage_mentor_assignments(request):

    if not request.user.is_superuser:
        return redirect("dashboard")

    mentors = MentorProfile.objects.select_related("user")

    search = request.GET.get("search")

    if search:
        mentors = mentors.filter(
            Q(user__username__icontains=search) |
            Q(name__istartswith=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )

    return render(
        request,
        "admin_module/manage_mentors/manage_assign_students.html",
        {
            "mentors": mentors,
        }
    )


@login_required(login_url="/users/login")
def assign_students(request, id):

    if not request.user.is_superuser:
        return redirect("dashboard")

    mentor = get_object_or_404(
        MentorProfile,
        id=id
    )

    students = StudentProfile.objects.select_related(
        "user"
    ).all()

    if request.method == "POST":

        selected_students = request.POST.getlist("students")

        # print("Selected students:", selected_students)
        # print("Mentor:", mentor)
        # print("Mentor ID:", mentor.id)

        # Remove previous assignments
        StudentProfile.objects.filter(
            mentor=mentor
        ).update(
            mentor=None
        )

        updated = StudentProfile.objects.filter(
            id__in=selected_students
        ).update(
            mentor=mentor
        )

        print("Rows updated:", updated)

        for student in StudentProfile.objects.filter(id__in=selected_students):
            print(student.full_name, "->", student.mentor)

        messages.success(
            request,
            "Students assigned successfully."
        )

        return redirect("manage_mentor_assignments")

    assigned_students = StudentProfile.objects.filter(
        mentor=mentor
    ).values_list(
        "id",
        flat=True
    )

    context = {
        "mentor": mentor,
        "students": students,
        "assigned_students": assigned_students,
    }

    return render(
        request,
        "admin_module/manage_mentors/assign_students.html",
        context
    )

@login_required(login_url='/users/login')
def manage_companies(request):

    if not request.user.is_superuser:
        return redirect('dashboard')

    companies = CompanyProfile.objects.select_related('user')

    search = request.GET.get('search')

    if search:
        companies = companies.filter(
            Q(user__username__icontains=search) |
            Q(name__istartswith=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )

    return render(request,'admin_module/manage_companies/manage_companies.html',{'companies': companies})

@login_required(login_url='/users/login')
def company_detail(request, id):

    if not request.user.is_superuser:
        return redirect('dashboard')

    company = get_object_or_404(
        CompanyProfile.objects.select_related('user'),
        id=id
    )

    total_jobs = Job.objects.filter(company=company).count()

    approved_jobs = Job.objects.filter(
    company=company,
    approval_status="Approved"
    ).count()

    pending_jobs = Job.objects.filter(
        company=company,
        approval_status="Pending"
    ).count()

    rejected_jobs = Job.objects.filter(
        company=company,
        approval_status="Rejected"
    ).count()

    context = {
        "company": company,
        "total_jobs": total_jobs,
        "approved_jobs": approved_jobs,
        "pending_jobs": pending_jobs,
        "rejected_jobs": rejected_jobs,
    }

    return render(request,"admin_module/manage_companies/company_details.html",context)

@login_required(login_url='/users/login')
def delete_company(request, id):

    if not request.user.is_superuser:
        messages.error(request, "You are not authorized.")
        return redirect("dashboard")

    company = get_object_or_404(CompanyProfile, id=id)

    if request.method == "POST":
        user = company.user
        user.delete()
        messages.success(request, "Company deleted successfully.")
        return redirect("manage_companies")

    return render(request, "admin_module/manage_companies/delete_company.html", {"company": company})

# ==============
# admin job management
# ===================

def admin_jobs(request):

    jobs = Job.objects.select_related(
        "company"
    ).order_by("-posted_on")


    return render(
        request,
        "admin_module/manage_job/jobs.html",
        {
            "jobs": jobs
        }
    )

def admin_job_detail(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    return render(
        request,
        "admin_module/manage_job/job_details.html",
        {
            "job": job
        }
    )
def delete_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    job.delete()

    messages.success(
        request,
        "Job deleted successfully"
    )

    return redirect("admin_jobs")

# ==================================
# mentor functions
# ====================================



@login_required(login_url="/users/login")
def my_students(request):

    if request.user.role != "mentor":
        return redirect("dashboard")

    mentor = get_object_or_404(
        MentorProfile,
        user=request.user
    )
    students = StudentProfile.objects.filter(
        mentor=mentor
    ).select_related(
        "user"
    )

    context = {
        "students": students
    }



    return render(
        request,
        "mentor_module/students/my_students.html",
        context
    )

@login_required(login_url="/users/login")
def mentor_student_progress(request, id):

    # Only mentors can access
    if request.user.role != "mentor":
        return redirect("dashboard")

    # Logged-in mentor
    mentor = get_object_or_404(
        MentorProfile,
        user=request.user
    )

    # Check whether this student is assigned to the logged-in mentor
    student = get_object_or_404(
        StudentProfile,
        id=id,
        mentor=mentor
    )

    # Get existing feedback (if any)
    feedback = MentorFeedback.objects.filter(
        mentor=mentor,
        student=student
    ).first()


    if request.method == "POST":

        text = request.POST.get("feedback")

        if feedback:

            feedback.feedback = text
            feedback.save()

        else:

            MentorFeedback.objects.create(
                mentor=mentor,
                student=student,
                feedback=text
            )
        messages.success(request, "Feedback saved successfully.")

        return redirect("my_students")


    # Current career
    career = StudentCareer.objects.filter(
        student=student
    ).first()

    # Career assessment report
    # Get the student's career conversation
    conversation = CareerConversation.objects.filter(
        student=student
    ).first()

    # Get the career assessment report
    report = None

    if conversation:
        report = CareerReport.objects.filter(
            conversation=conversation
        ).first()

    # Roadmap
    roadmap = CareerRoadmap.objects.filter(
        student=student
    ).first()

    # Skill gap
    skill_gap = SkillGap.objects.filter(
        student=student
    ).first()

    # Job applications
    applications = JobApplication.objects.filter(
        student=student
    )

    applied = applications.count()
    shortlisted = applications.filter(status="accepted").count()
    rejected = applications.filter(status="rejected").count()
    pending = applications.filter(status="pending").count()

    context = {
        "student": student,
        "career": career,
        "report": report,
        "roadmap": roadmap,
        "skill_gap": skill_gap,
        "applied": applied,
        "shortlisted": shortlisted,
        "rejected": rejected,
        "pending": pending,
        "feedback": feedback,
    }

    return render(
        request,
        "mentor_module/mentor_student_progress.html",
        context,
    )

@login_required
def resume_evaluation(request):

    if request.user.role != "mentor":
        return redirect("dashboard")

    mentor = get_object_or_404(
        MentorProfile,
        user=request.user
    )
    search = request.GET.get("search", "")
    students = StudentProfile.objects.filter(
        mentor=mentor
    ).select_related(
        "user"
    )
    if search:
        students = students.filter(
            Q(full_name__icontains=search) |
            Q(full_name__istartswith=search) |
            Q(user__email__icontains=search) |
            Q(user__username__icontains=search)
        )

    return render(
        request,
        "mentor_module/resume_evaluation.html",
        {
            "students": students,
            "search": search,
        }
    )

@login_required
def evaluate_resume(request, resume_id):

    resume = get_object_or_404(
        Resume,
        id=resume_id
    )

    student = resume.student

    if request.method == "POST":

        resume.mentor_feedback = request.POST.get("feedback")
        resume.feedback_date = timezone.now()
        resume.save()

        messages.success(request, "Resume feedback saved successfully.")

        return redirect(
            "student_resumes",
            student_id=resume.student.user.id
        )

    return render(
        request,
        "mentor_module/evaluate_resume.html",
        {
            "resume": resume,
            "student": student,
        },
    )

@login_required
def mentor_resume_preview(request, resume_id):

    resume = get_object_or_404(Resume,id=resume_id)
    student = resume.student

    if resume.template == "professional":
        template_name = "mentor_module/resume/professional_resume.html"

    elif resume.template == "modern":
        template_name = "mentor_module/resume/modern_resume.html"

    else:
        template_name = "mentor_module/resume/minimal_resume.html"

    context = get_resume_data(resume)

    context["resume"] = resume
    context["student"] = student

    return render(
        request,
        template_name,
        context
    )

@login_required
def student_resumes(request, student_id):

    student = get_object_or_404(
        StudentProfile,
        id=student_id
    )

    resumes = Resume.objects.filter(
        student=student
    ).order_by("-created_at")

    return render(
        request,
        "mentor_module/student_resumes.html",
        {
            "student": student,
            "resumes": resumes,
        }
    )

# =================================
# mentor interview evaluation
# ==================================

@login_required
def mock_interview_students(request):

    students = StudentProfile.objects.all()

    search = request.GET.get("search")

    if search:
            students = students.filter(
                Q(full_name__icontains=search) |
                Q(full_name__istartswith=search) |
                Q(user__email__icontains=search) |
                Q(user__username__icontains=search)
            )

    return render(
        request,
        "mentor_module/mock_interview_students.html",
        {
            "students": students
        }
    )

@login_required
def student_mock_interviews(request, student_id):

    student = get_object_or_404(
        StudentProfile,
        id=student_id
    )

    interviews = MockInterview.objects.filter(
        student=student
    ).order_by("-created_at")

    return render(
        request,
        "mentor_module/student_mock_interviews.html",
        {
            "student": student,
            "interviews": interviews
        }
    )

@login_required
def view_interview_report(request, interview_id):

    interview = get_object_or_404(
        MockInterview,
        id=interview_id
    )

    return render(
        request,
        "mentor_module/view_interview_report.html",
        {
            "interview": interview
        }
    )

@login_required
def mentor_interview_feedback(request, interview_id):

    interview = get_object_or_404(
        MockInterview,
        id=interview_id
    )

    if request.method == "POST":

        interview.mentor_feedback = request.POST.get("feedback")

        interview.feedback_date = timezone.now()

        interview.save()

        messages.success(
            request,
            "Feedback Saved Successfully."
        )

        return redirect(
            "student_mock_interviews",
            interview.student.id
        )

    return render(
        request,
        "mentor_module/interview_feedback.html",
        {
            "interview": interview
        }
    )

# ======================
# admin pending job 
# ======================

def pending_jobs(request):

    jobs = Job.objects.filter(
        approval_status="Pending"
    ).order_by("-posted_on")


    return render(
        request,
        "admin_module/manage_job/pending_jobs.html",
        {
            "jobs": jobs
        }
    )

# ===================
# admin job view
# ===================


def admin_job_detail(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    return render(
        request,
        "admin_module/manage_job/admin_job_details.html",
        {
            "job": job
        }
    )

# ===============================
# admin approve and reject job
# ==============================

def approve_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    job.approval_status = "Approved"

    job.save()


    messages.success(
        request,
        "Job approved successfully!"
    )


    return redirect("pending_jobs")

def reject_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )


    job.approval_status = "Rejected"

    job.save()


    messages.warning(
        request,
        "Job rejected!"
    )


    return redirect("pending_jobs")

# =====================
# admin add functions
# ========================

def add_student(request):

    if request.method == "POST":

        form = StudentForm(request.POST, request.FILES)

        if form.is_valid():

            user = CustomUser.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                role="student",
            )

            student = form.save(commit=False)
            student.user = user
            student.save()

            messages.success(request, "Student added successfully.")
            return redirect("admin_dashboard")

    else:
        form = StudentForm()

    return render(request, "admin_module/quick_actions/add_student.html", {"form": form})


def add_mentor(request):

    if request.method == "POST":

        form = MentorForm(request.POST, request.FILES)

        if form.is_valid():

            user = CustomUser.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                role="mentor",
            )

            mentor = form.save(commit=False)
            mentor.user = user
            mentor.save()

            messages.success(request, "Mentor added successfully.")
            return redirect("admin_dashboard")

    else:
        form = MentorForm()

    return render(request, "admin_module/quick_actions/add_mentor.html", {"form": form})


def add_company(request):

    if request.method == "POST":

        form = CompanyForm(request.POST)

        if form.is_valid():

            user = CustomUser.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                role="company",
            )

            company = form.save(commit=False)
            company.user = user
            company.save()

            messages.success(request, "Company added successfully.")
            return redirect("admin_dashboard")

    else:
        form = CompanyForm()

    return render(request, "admin_module/quick_actions/add_company.html", {"form": form})

# ===========================
# student learning platform
# ===========================

@login_required
def learning_platform(request):

    student = StudentProfile.objects.get(user=request.user)

    try:
        career = StudentCareer.objects.get(
            student=student,
            active=True
        )
    except StudentCareer.DoesNotExist:
        messages.warning(request, "Please select a career first.")
        return redirect("career_assessment")

    prompt = f"""
You are an AI Career Mentor.

The student's selected career is: {career.career_name}

Recommend exactly 10 FREE online courses that are relevant to this career.

IMPORTANT RULES:

1. Recommend only well-known courses from trusted platforms.
2. Never invent or guess a course URL.
3. If you are not 100% certain of the exact course URL, write:
Learning Link: Official Website
4. Prefer these providers:
- Coursera
- edX
- Microsoft Learn
- Google Developers
- Kaggle Learn
- Cisco Skills for All
- Codecademy
- W3Schools
- freeCodeCamp
- Harvard CS50

For each course output exactly in this format:

Course Name:
Provider:
Difficulty:
Duration:
Learning Link:

After each course write:

###END###

Do not use markdown.
Do not use tables.
Do not add explanations.
Do not generate fake URLs.
If unsure about the exact URL, always write:
Learning Link: Official Website
"""

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    text = response["message"]["content"]

    courses = []

    for course in text.split("###END###"):
        course = course.strip()
        if course:
            courses.append(course)

    return render(
        request,
        "student_module/learning/learning_platform.html",
        {
            "career": career,
            "courses": courses,
        },
    )



@login_required
def career_progress(request):

    tasks = CareerTask.objects.filter(
        student=request.user
    ).order_by("-created_at")

    total = tasks.count()

    completed = tasks.filter(
        completed=True
    ).count()

    progress = 0

    if total > 0:
        progress = int((completed / total) * 100)

    context = {
        "tasks": tasks,
        "total": total,
        "completed": completed,
        "progress": progress,
    }

    return render(
        request,
        "student_module/career_progress/career_progress.html",
        context,
    )

@login_required
def add_task(request):

    if request.method == "POST":

        form = CareerTaskForm(request.POST)

        if form.is_valid():

            task = form.save(commit=False)

            task.student = request.user

            task.save()

            return redirect("career_progress")

    else:

        form = CareerTaskForm()

    return render(
        request,
        "student_module/career_progress/add_task.html",
        {
            "form": form
        },
    )

@login_required
def toggle_task(request, task_id):

    task = get_object_or_404(
        CareerTask,
        id=task_id,
        student=request.user
    )

    task.completed = not task.completed

    task.save()

    return redirect("career_progress")

@login_required
def edit_task(request, task_id):

    task = get_object_or_404(
        CareerTask,
        id=task_id,
        student=request.user
    )

    if request.method == "POST":

        form = CareerTaskForm(
            request.POST,
            instance=task
        )

        if form.is_valid():

            form.save()

            return redirect("career_progress")

    else:

        form = CareerTaskForm(instance=task)

    return render(
        request,
        "student_module/career_progress/edit_task.html",
        {
            "form": form
        },
    )

@login_required
def delete_task(request, task_id):

    task = get_object_or_404(
        CareerTask,
        id=task_id,
        student=request.user
    )

    task.delete()

    return redirect("career_progress")
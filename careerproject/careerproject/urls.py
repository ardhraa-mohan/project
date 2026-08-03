"""
URL configuration for careerproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from careerproject import views


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Common Pages
    path('', views.home, name='home'),
    path('features/', views.feature, name='feature'),
    path('work/', views.workpage, name='work'),
    path('about/', views.aboutpage, name='about'),
    path('contact/', views.contactpage, name='contact'),
    path('pri/', views.privatepage, name='pri'),
    path('mentors/', views.mentors, name='mentors'),
    
    # Authentication
    path('login/', views.loginpage, name='login'),
    path('logout/', views.logoutpage, name='logout'),
    path('register/', views.registerpage, name='register'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/mentor/', views.mentor_register, name='mentor_register'),
    path('register/company/', views.company_register, name='company_register'),
    # path("forgot-password/", views.forgot_password, name="forgot_password"),
    # path("verify-otp/", views.verify_otp, name="verify_otp"),
    # path("reset-password/", views.reset_password, name="reset_password"),
    
    # Dashboard
    path('dashredirect/', views.dashboard, name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('mentordash/', views.mentor_dashboard, name='mentor_dashboard'),
    path('companydash/', views.company_dashboard, name='company_dashboard'),
    path('admindash/', views.admin_dashboard, name='admin_dashboard'),
    
    
    # Student Profile
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/profile/edit/', views.edit_student_profile, name='edit_student_profile'),
    
    
    # Mentor Profile
    path('mentor/profile/', views.mentor_profile, name='mentor_profile'),
    path('mentor/profile/edit/', views.edit_mentor_profile, name='edit_mentor_profile'),
    
    
    # Company Profile
    path('company/profile/', views.company_profile, name='company_profile'),
    path('company/profile/edit/', views.edit_company_profile, name='edit_company_profile'),
    
    
    # Communication
    # path('notification/', views.notificationpage, name='notification'),
    path('subscription/', views.subscription, name='subscription'),
    # path('mentornotifi/', views.mentornotificationpage, name='mentornotifi'),
    path('mentorstu/', views.mentorstudentpage, name='mentorstudent'),
    
    
    # Jobs
    path('postjob/', views.post_job, name='post_Job'),
    path("myjobs/", views.my_jobs, name="my_jobs"),
    path("managejobs/", views.manage_jobs, name="manage_jobs"),
    path("viewjob/<int:id>/", views.view_job, name="view_job"),
    path("editjob/<int:id>/", views.edit_job, name="edit_job"),
    path("deletejob/<int:id>/", views.delete_job, name="delete_job"),
    path("close-job/<int:job_id>/", views.close_job, name="close_job"),
    path("open-job/<int:job_id>/", views.open_job, name="open_job"),
    path("jobportal/", views.job_portal, name="job_portal"),
    path("jobdetails/<int:id>/", views.job_details, name="job_details"),
    
    
    # Applications
    path("job/<int:id>/apply/", views.apply_job, name="apply_job"),
    path("my-applications/", views.my_applications, name="my_applications"),
    

    # Recruitment
    path("company/applicants/", views.company_applicants, name="company_applicants"),
    path("company/job/<int:job_id>/", views.view_applicants, name="view_applicants"),
    path("resume/<int:application_id>/", views.company_resume_view, name="company_resume_view"),
    path("application/<int:id>/", views.view_application, name="view_application"),
    path("company/shortlisted-candidates/", views.shortlisted_candidates, name="shortlisted_candidates"),
    
    
    # Resume Builder
    path("resume/", views.resume_dashboard, name="resume_dashboard"),
    path("resume/feedback/",views.resume_feedback,name="resume_feedback"),
    path('resumebuilder/', views.resume_builder, name='resume_builder'),
    path("resume/<int:id>/personal-details/", views.resume_personal_details, name="resume_personal_details"),
    path("student/resume/<int:id>/education/", views.resume_education, name="resume_education"),
    path("resume/education/<int:id>/edit/", views.edit_education, name="edit_education"),
    path("resume/education/<int:id>/delete/", views.delete_education, name="delete_education"),
    path("resume/<int:id>/projects/", views.resume_projects, name="resume_projects"),
    path("resume/project/<int:id>/edit/", views.edit_project, name="edit_project"),
    path("resume/project/<int:id>/delete/", views.delete_project, name="delete_project"),
    path("resume/<int:id>/skills/", views.resume_skills, name="resume_skills"),
    path("resume/<int:id>/experience/", views.resume_experience, name="resume_experience"),
    path("resume/experience/<int:id>/edit/", views.edit_experience, name="edit_experience"),
    path("resume/experience/<int:id>/delete/", views.delete_experience, name="delete_experience"),
    path("resume/<int:id>/preview/", views.resume_preview, name="resume_preview"),
    path("resume/<int:id>/pdf/", views.resume_pdf, name="resume_pdf"),
    path("resume/<int:resume_id>/preview/apply/<int:job_id>/", views.resume_preview_apply, name="resume_preview_apply"),
    path("resume/finish/<int:id>/",views.finish_resume,name="finish_resume",),
    path('resume/delete/<int:id>/', views.delete_resume, name='delete_resume'),
    path(
    "resume/view/<int:resume_id>/",views.feedback_view_resume,name="feedback_view_resume",),

    
    
    # Career Guidance
    path("career/assessment/", views.career_assessment, name="career_assessment"),
    path("generate-report/<int:id>/", views.generate_career_report, name="generate_career_report"),
    path("report/<int:id>/", views.career_report, name="career_report"),
    path("select-career/<path:career_name>/", views.select_career, name="select_career"),
    path("change-career/", views.change_career, name="change_career"),
    path("confirm-change-career/", views.confirm_change_career, name="confirm_change_career"),
    path("retake-assessment/", views.retake_assessment, name="retake_assessment"),
    

    # Career Roadmap
    path("roadmap/", views.roadmap, name="career_roadmap"),
    
    
    # Skill Gap
    path('career-skillgap', views.skill_gap, name='skill_gap'),
    
    
    # Mock Interview
    path("mock-interview/", views.mock_interview, name="mock_interview"),
    path("mock-interview/start/", views.start_mock_interview, name="start_mock_interview"),
    path("mock-interview/question/<int:pk>/", views.interview_question, name="interview_question"),
    path("mock-interview/report/<int:pk>/", views.interview_report, name="interview_report"),
    path("mock-interview/history/", views.interview_history, name="interview_history"),
    path("mock-interview/feedback/",views.student_interview_feedback,name="student_interview_feedback",),

    
    
    # Chat
    path("mymentor/", views.my_mentor, name="my_mentor"),
    

    # mentor feedback view
    path("mentor-feedback/",views.mentor_feedback,name="mentor_feedback",),
    
    # Admin Panel
    path('students/', views.manage_students, name='manage_students'),
    path("students/<int:id>/", views.student_detail, name="student_details"),
    path("students/delete/<int:id>/", views.delete_student, name="delete_student"),
    path('manage_mentors/', views.manage_mentors, name='manage_mentors'),
    path("mentors/<int:id>/", views.mentor_detail, name="mentor_detail"),
    path("mentors/delete/<int:id>/", views.delete_mentor, name="delete_mentor"),
    path("manage-assign-students/",views.manage_mentor_assignments,name="manage_mentor_assignments",),

    path("assign-students/<int:id>/",views.assign_students,name="assign_students",),
    path('companies/', views.manage_companies, name='manage_companies'),
    path("companies/<int:id>/", views.company_detail, name="company_detail"),
    path("companies/delete/<int:id>/", views.delete_company, name="delete_company"),

    # admin job management
    path("jobs/", views.admin_jobs, name="admin_jobs"),
    path("jobs/<int:job_id>/", views.admin_job_detail, name="admin_job_detail"),
    path("jobs/delete/<int:job_id>/", views.delete_job, name="delete_job"),

    # admin job pending
    path("pending-jobs/",views.pending_jobs,name="pending_jobs"),

    # admin job details view
    path("jobs/<int:job_id>/",views.admin_job_detail,name="admin_job_detail"),

    # admin approve or reject job
    path("approve-job/<int:job_id>/",views.approve_job,name="approve_job"),
    path("reject-job/<int:job_id>/",views.reject_job,name="reject_job"),

    # admin add functions
    path("students/add/", views.add_student, name="add_student"),
    path("mentors/add/", views.add_mentor, name="add_mentor"),
    path("companies/add/", views.add_company, name="add_company"),


    # mentor functions
    path("my-students/",views.my_students,name="my_students"),
    path("mentorstudentpro/<int:id>/",views.mentor_student_progress,name="mentor_student_progress",),
    path("mentor/resume-evaluation/",views.resume_evaluation,name="resume_evaluation",),
    path("mentor/evaluate-resume/<int:resume_id>/",views.evaluate_resume,name="evaluate_resume",),
    path("mentor/student-resumes/<int:student_id>/",views.student_resumes,name="student_resumes",), 
    path("mentor/resume-preview/<int:resume_id>/",views.mentor_resume_preview,name="mentor_resume_preview",),
    path("mock-interview-evaluation/",views.mock_interview_students,name="mock_interview_students",),
    path("student-interviews/<int:student_id>/",views.student_mock_interviews,name="student_mock_interviews",),
    path("view-interview-report/<int:interview_id>/",views.view_interview_report,name="view_interview_report",),
    path("interview-feedback/<int:interview_id>/",views.mentor_interview_feedback,name="mentor_interview_feedback",),   

    # mentor chat
    path("mentor/chats/",views.mentor_chat_list,name="mentor_chat_list",),
    path("mentor/chat/<int:room_id>/",views.mentor_chat,name="mentor_chat",),

    # student learning platform function
    path("learning/",views.learning_platform,name="learning_platform",),

    # career progress todo app
    path("career-progress/",views.career_progress,name="career_progress",),
    path("career-progress/add/",views.add_task,name="add_task",),
    path("career-progress/<int:task_id>/toggle/",views.toggle_task,name="toggle_task",),
    path("career-progress/<int:task_id>/edit/",views.edit_task,name="edit_task",),
    path("career-progress/<int:task_id>/delete/",views.delete_task,name="delete_task",),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
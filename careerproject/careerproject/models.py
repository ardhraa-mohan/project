from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth import get_user_model

# ============================================
# USER MODULE
# ============================================

class CustomUser(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('company', 'Company'),
    )
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='student')

# ============================================
# STUDENT MODULE
# ============================================

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    mentor = models.ForeignKey('MentorProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    # Personal Details
    profile_pic = models.ImageField(upload_to='students/', blank=True, null=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15,)
    GENDER_CHOICES = (
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
    )
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES)
    dob = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)

    # Education
    QUALIFICATION_CHOICES=(
            ('10th', '10th'),
            ('12th', '12th'),
            ('Diploma', 'Diploma'),
            ('Graduate', 'Graduate'),
            ('Post Graduate', 'Post Graduate'),
            ('Others', 'Others'),
    )
    qualification = models.CharField(max_length=30, choices=QUALIFICATION_CHOICES)
    course = models.CharField(max_length=100)

    # Career Details
    OCCUPATIONAL_CHOICES=(
            ('Student', 'Student'),
            ('Unemployed', 'Unemployed'),
            ('Employed', 'Employed'),
            ('Career Break', 'Career Break'),
    )
    occupational_status = models.CharField(max_length=20, choices=OCCUPATIONAL_CHOICES)

    # Skills
    skills = models.TextField()

    # Documents
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    # About
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.full_name or self.user.username


class Resume(models.Model):

    TEMPLATE_CHOICES = (
        ('professional', 'Professional'),
        ('modern', 'Modern'),
        ('minimal', 'Minimal'),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='generated_resumes')
    resume_name = models.CharField(max_length=100)
    target_job = models.ForeignKey('Job', on_delete=models.CASCADE)
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='professional')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    mentor_feedback = models.TextField(blank=True, null=True)
    feedback_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.resume_name
    
class ResumePersonal(models.Model):

    resume = models.OneToOneField(Resume, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
    
class ResumeEducation(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=100)
    institution = models.CharField(max_length=150)
    university = models.CharField(max_length=150)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    cgpa = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.qualification
    

class ResumeProject(models.Model):

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    project_title = models.CharField(max_length=150)
    technologies = models.CharField(max_length=200)
    description = models.TextField()
    github_link = models.URLField(blank=True, null=True)
    live_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.project_title
    
class ResumeSkill(models.Model):

    resume = models.ForeignKey(Resume, related_name="skills", on_delete=models.CASCADE)

    technical_skills = models.TextField(blank=True, null=True)
    soft_skills = models.TextField(blank=True, null=True)
    languages = models.TextField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Skills - {self.resume.resume_name}"
    
class ResumeExperience(models.Model):

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)

    job_title = models.CharField(max_length=100)

    company_name = models.CharField(max_length=100)

    location = models.CharField(max_length=100, blank=True)

    start_date = models.CharField(max_length=20)

    end_date = models.CharField(max_length=20, blank=True)

    currently_working = models.BooleanField(default=False)

    description = models.TextField()

    def __str__(self):
        return f"{self.job_title} - {self.company_name}"

# ============================================
# MENTOR MODULE
# ============================================

class MentorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    profile_pic = models.ImageField(upload_to='mentors/', blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True)
    
    phone = models.CharField(max_length=15, blank=True)
    GENDER_CHOICES = (
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)

    QUALIFICATION_CHOICES = (
    ('Diploma', 'Diploma'),
    ('BCA', 'BCA'),
    ('B.Sc', 'B.Sc'),
    ('B.Tech', 'B.Tech'),
    ('BE', 'BE'),
    ('B.Com', 'B.Com'),
    ('BA', 'BA'),
    ('MCA', 'MCA'),
    ('M.Sc', 'M.Sc'),
    ('M.Tech', 'M.Tech'),
    ('MBA', 'MBA'),
    ('PhD', 'PhD'),
    ('Other', 'Other'),
    )
    qualification = models.CharField(max_length=100, choices=QUALIFICATION_CHOICES, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    experience = models.PositiveIntegerField(default=0)
    company = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return self.user.username




# ============================================
# COMPANY MODULE
# ============================================

class CompanyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    company_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    INDUSTRY_CHOICES = (
    ('IT', 'Information Technology'),
    ('Finance', 'Finance'),
    ('Healthcare', 'Healthcare'),
    ('Education', 'Education'),
    ('E-Commerce', 'E-Commerce'),
    ('Manufacturing', 'Manufacturing'),
    ('Telecommunications', 'Telecommunications'),
    ('Marketing', 'Marketing'),
    ('Other', 'Other'),
    )
    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES, blank=True)

    def __str__(self):
        return self.company_name
    
class Job(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)

    job_title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    STATUS_CHOICES = (
    ('Open', 'Open'),
    ('Closed', 'Closed'),
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open'
    )

    JOBTYPE_CHOICES = (
            ('Full Time', 'Full Time'),
            ('Part Time', 'Part Time'),
            ('Internship', 'Internship'),
            ('Remote', 'Remote'),
    )
    job_type = models.CharField(max_length=20, choices=JOBTYPE_CHOICES)
    salary = models.CharField(max_length=50, blank=True)
    skills_required = models.TextField()
    deadline = models.DateField()
    posted_on = models.DateTimeField(auto_now_add=True)
    APPROVAL_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default='Pending'
    )
    def __str__(self):
        return self.job_title

# ============================================
# APPLICATIONS MODULE
# ============================================

class JobApplication(models.Model):

    STATUS_CHOICES = (
        ("Applied", "Applied"),
        ("Shortlisted", "Shortlisted"),
        ("Selected", "Selected"),
        ("Rejected", "Rejected"),
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Applied"
    )

    class Meta:
        unique_together = ("student", "job")

    def __str__(self):
        return f"{self.student.full_name} - {self.job.job_title}"

# ============================================
# CAREER GUIDANCE MODULE
# ============================================

class CareerConversation(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    started_at = models.DateTimeField(auto_now_add=True)

    completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.student.full_name
    

class CareerMessage(models.Model):

    conversation = models.ForeignKey(
        CareerConversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    ROLE = (
        ("assistant", "Assistant"),
        ("student", "Student"),
    )

    sender = models.CharField(
        max_length=20,
        choices=ROLE
    )

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

class CareerReport(models.Model):

    conversation = models.OneToOneField(
        CareerConversation,
        on_delete=models.CASCADE
    )

    report = models.TextField(blank=True,
    null=True)
    recommended_careers = models.JSONField(
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)


class StudentCareer(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="careers"
    )

    career_name = models.CharField(max_length=100)

    confidence = models.PositiveIntegerField(default=0)

    active = models.BooleanField(default=True)

    selected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.career_name}"

# ============================================
# CAREER ROADMAP MODULE
# ============================================

class CareerRoadmap(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    career = models.ForeignKey(
        StudentCareer,
        on_delete=models.CASCADE
    )

    roadmap = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.student.full_name} - {self.career.career_name}"

# ============================================
# SKILL GAP MODULE
# ============================================

class SkillGap(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    career = models.ForeignKey(
        StudentCareer,
        on_delete=models.CASCADE
    )

    report = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.student.full_name

# ============================================
# MOCK INTERVIEW MODULE
# ============================================

class MockInterview(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    career = models.ForeignKey(
        StudentCareer,
        on_delete=models.CASCADE
    )

    difficulty = models.CharField(
        max_length=20
    )

    total_questions = models.IntegerField(default=10)

    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    overall_score = models.IntegerField(default=0)

    technical_score = models.IntegerField(default=0)

    communication_score = models.IntegerField(default=0)

    confidence_score = models.IntegerField(default=0)

    ai_report = models.TextField(blank=True)

    mentor_feedback = models.TextField(blank=True,null=True)

    feedback_date = models.DateTimeField(blank=True,null=True)
    

    def __str__(self):
        return f"{self.student.full_name} - {self.career.career_name}"
        

class InterviewQuestion(models.Model):

    interview = models.ForeignKey(
        MockInterview,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question = models.TextField()

    answer = models.TextField(
        blank=True
    )

    feedback = models.TextField(
        blank=True
    )

    marks = models.IntegerField(
        default=0
    )

    order = models.IntegerField()

    def __str__(self):
        return f"Question {self.order}"

# ============================================
# CHAT MODULE
# ============================================


class ChatRoom(models.Model):

    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="chat_room"
    )

    mentor = models.ForeignKey(
        MentorProfile,
        on_delete=models.CASCADE,
        related_name="chat_rooms"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.student.full_name} ↔ {self.mentor.full_name}"


class Message(models.Model):

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    text = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_read = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username} - {self.created_at:%d/%m/%Y %H:%M}"


# ============================
# mentor feedback
# ============================

class MentorFeedback(models.Model):

    mentor = models.ForeignKey(
        MentorProfile,
        on_delete=models.CASCADE
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    feedback = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.student.full_name} - Feedback"





User = get_user_model()
class CareerTask(models.Model):

    CATEGORY_CHOICES = [
        ('Learning', 'Learning'),
        ('Resume', 'Resume'),
        ('Interview', 'Interview'),
        ('Job', 'Job'),
        ('Personal', 'Personal'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='Learning'
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    completed = models.BooleanField(default=False)

    auto_generated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

#     from django.contrib.auth import get_user_model is used to get your project's User model.

# Since your CareerPilot project most likely has a custom user model (e.g., CustomUser with roles like Student, Mentor, Company, Admin), you should not directly import Django's default User.
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('candidate', 'Job Seeker'),
        ('employer', 'Employer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=255)
    logo_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.company_name

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated skills")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class JobListing(models.Model):
    JOB_TYPES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    )
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(help_text="Requirements list (one per line)")
    location = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=100, blank=True, help_text="e.g., $80,000 - $100,000")
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='full_time')
    category = models.CharField(max_length=100, default='Software Development')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewing', 'Reviewing'),
        ('shortlisted', 'Shortlisted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ('job', 'candidate')
        
    def __str__(self):
        return f"{self.candidate.username} -> {self.job.title} ({self.status})"

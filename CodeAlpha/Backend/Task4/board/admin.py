from django.contrib import admin
from .models import UserProfile, EmployerProfile, CandidateProfile, JobListing, JobApplication

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'location', 'website')
    search_fields = ('company_name', 'location')

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills')
    search_fields = ('user__username', 'skills')

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'job_type', 'category', 'location', 'created_at', 'is_active')
    list_filter = ('job_type', 'category', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'location')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'candidate', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('job__title', 'candidate__username')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q

from .models import UserProfile, EmployerProfile, CandidateProfile, JobListing, JobApplication

def index_view(request):
    # Search filters
    q = request.GET.get('q', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('type', '')
    category = request.GET.get('category', '')
    
    jobs = JobListing.objects.filter(is_active=True).order_by('-created_at')
    
    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if category:
        jobs = jobs.filter(category=category)
        
    # Get distinct categories & locations for dropdowns
    categories = JobListing.objects.values_list('category', flat=True).distinct()
    locations = JobListing.objects.values_list('location', flat=True).distinct()
    
    context = {
        'jobs': jobs,
        'q': q,
        'selected_location': location,
        'selected_type': job_type,
        'selected_category': category,
        'categories': categories,
        'locations': locations,
        'job_types': JobListing.JOB_TYPES,
    }
    return render(request, 'board/index.html', context)

def job_detail_view(request, pk):
    job = get_object_or_404(JobListing, pk=pk)
    has_applied = False
    application_status = None
    
    if request.user.is_authenticated:
        app = JobApplication.objects.filter(job=job, candidate=request.user).first()
        if app:
            has_applied = True
            application_status = app.get_status_display()
            
    # Format requirements list
    requirements = [r.strip() for r in job.requirements.split('\n') if r.strip()]
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'application_status': application_status,
        'requirements': requirements,
    }
    return render(request, 'board/job_detail.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'candidate')
        
        # Role-specific fields
        company_name = request.POST.get('company_name', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'board/register.html')
            
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            UserProfile.objects.create(user=user, role=role)
            
            if role == 'employer':
                EmployerProfile.objects.create(
                    user=user,
                    company_name=company_name or f"{username}'s Company"
                )
            else:
                CandidateProfile.objects.create(user=user)
                
            login(request, user)
            messages.success(request, f"Welcome, {username}! Your account has been created.")
            return redirect('dashboard')
        except IntegrityError:
            messages.error(request, "Username is already taken.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            
    return render(request, 'board/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'board/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('index')

@login_required
def dashboard_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if user_profile.role == 'employer':
        # Employer dashboard view
        try:
            emp_profile = request.user.employer_profile
        except EmployerProfile.DoesNotExist:
            emp_profile = EmployerProfile.objects.create(user=request.user, company_name=f"{request.user.username}'s Company")
            
        jobs = JobListing.objects.filter(employer=request.user).order_by('-created_at')
        applications = JobApplication.objects.filter(job__employer=request.user).order_by('-applied_at')
        
        # Calculate stats
        total_jobs = jobs.count()
        total_apps = applications.count()
        pending_apps = applications.filter(status='pending').count()
        shortlisted_apps = applications.filter(status='shortlisted').count()
        
        context = {
            'role': 'employer',
            'emp_profile': emp_profile,
            'jobs': jobs,
            'applications': applications,
            'total_jobs': total_jobs,
            'total_apps': total_apps,
            'pending_apps': pending_apps,
            'shortlisted_apps': shortlisted_apps,
            'status_choices': JobApplication.STATUS_CHOICES,
        }
        return render(request, 'board/employer_dashboard.html', context)
    else:
        # Candidate dashboard view
        try:
            cand_profile = request.user.candidate_profile
        except CandidateProfile.DoesNotExist:
            cand_profile = CandidateProfile.objects.create(user=request.user)
            
        applications = JobApplication.objects.filter(candidate=request.user).order_by('-applied_at')
        
        # Parse skills
        skills_list = [s.strip() for s in cand_profile.skills.split(',') if s.strip()] if cand_profile.skills else []
        
        context = {
            'role': 'candidate',
            'cand_profile': cand_profile,
            'skills_list': skills_list,
            'applications': applications,
        }
        return render(request, 'board/candidate_dashboard.html', context)

@login_required
def profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.role == 'employer':
        emp_profile, _ = EmployerProfile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            emp_profile.company_name = request.POST.get('company_name', emp_profile.company_name)
            emp_profile.website = request.POST.get('website', emp_profile.website)
            emp_profile.location = request.POST.get('location', emp_profile.location)
            emp_profile.logo_url = request.POST.get('logo_url', emp_profile.logo_url)
            emp_profile.description = request.POST.get('description', emp_profile.description)
            emp_profile.save()
            
            # Save user first/last names
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.save()
            
            messages.success(request, "Company profile updated successfully.")
            return redirect('dashboard')
            
        context = {
            'role': 'employer',
            'emp_profile': emp_profile,
        }
        return render(request, 'board/profile.html', context)
    else:
        cand_profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            cand_profile.bio = request.POST.get('bio', cand_profile.bio)
            cand_profile.skills = request.POST.get('skills', cand_profile.skills)
            cand_profile.education = request.POST.get('education', cand_profile.education)
            cand_profile.experience = request.POST.get('experience', cand_profile.experience)
            
            if 'resume' in request.FILES:
                cand_profile.resume = request.FILES['resume']
                
            cand_profile.save()
            
            # Save user first/last names
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.save()
            
            messages.success(request, "Candidate profile updated successfully.")
            return redirect('dashboard')
            
        context = {
            'role': 'candidate',
            'cand_profile': cand_profile,
        }
        return render(request, 'board/profile.html', context)

@login_required
def post_job_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.role != 'employer':
        messages.error(request, "Only employers can post jobs.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        location = request.POST.get('location')
        salary_range = request.POST.get('salary_range')
        job_type = request.POST.get('job_type', 'full_time')
        category = request.POST.get('category', 'Software Development')
        
        if not title or not description or not location:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'board/post_job.html', {'job_types': JobListing.JOB_TYPES})
            
        JobListing.objects.create(
            employer=request.user,
            title=title,
            description=description,
            requirements=requirements,
            location=location,
            salary_range=salary_range,
            job_type=job_type,
            category=category
        )
        messages.success(request, f"Job '{title}' posted successfully!")
        return redirect('dashboard')
        
    return render(request, 'board/post_job.html', {'job_types': JobListing.JOB_TYPES})

@login_required
def apply_job_view(request, job_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.role != 'candidate':
        messages.error(request, "Only candidates can apply for jobs.")
        return redirect('job_detail', pk=job_id)
        
    job = get_object_or_404(JobListing, pk=job_id)
    cand_profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, candidate=request.user).exists():
            messages.warning(request, "You have already applied for this job.")
            return redirect('job_detail', pk=job_id)
            
        # Optional: update resume on application if new file uploaded
        app_resume = cand_profile.resume
        if 'resume' in request.FILES:
            cand_profile.resume = request.FILES['resume']
            cand_profile.save()
            app_resume = cand_profile.resume
            
        JobApplication.objects.create(
            job=job,
            candidate=request.user,
            cover_letter=cover_letter,
            resume=app_resume
        )
        messages.success(request, f"Application for '{job.title}' submitted successfully!")
        return redirect('dashboard')
        
    context = {
        'job': job,
        'cand_profile': cand_profile,
    }
    return render(request, 'board/apply_job.html', context)

@login_required
@require_POST
def update_application_status(request, app_id):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.role != 'employer':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
    application = get_object_or_404(JobApplication, pk=app_id, job__employer=request.user)
    new_status = request.POST.get('status')
    
    valid_statuses = [choice[0] for choice in JobApplication.STATUS_CHOICES]
    if new_status in valid_statuses:
        application.status = new_status
        application.save()
        
        # Simple local JSON response for AJAX updates
        return JsonResponse({
            'success': True,
            'new_status': application.get_status_display(),
            'status_code': application.status
        })
    return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

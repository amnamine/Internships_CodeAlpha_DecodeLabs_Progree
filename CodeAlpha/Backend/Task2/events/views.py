from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Category, Event, Registration
from .forms import SignUpForm, EventForm
from django.contrib.auth.forms import AuthenticationForm

def home(request):
    categories = Category.objects.all()
    events = Event.objects.all().order_by('date', 'time')

    # Filtering and searching
    search_query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')

    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if category_slug:
        events = events.filter(category__slug=category_slug)

    context = {
        'categories': categories,
        'events': events,
        'search_query': search_query,
        'selected_category': category_slug,
    }
    return render(request, 'events/home.html', context)

def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    
    is_registered = False
    registration = None
    if request.user.is_authenticated:
        registration = Registration.objects.filter(event=event, user=request.user).first()
        is_registered = registration is not None and registration.status == 'Confirmed'

    context = {
        'event': event,
        'is_registered': is_registered,
        'registration': registration,
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def register_event(request, slug):
    event = get_object_or_404(Event, slug=slug)

    if request.method == 'POST':
        if event.is_past:
            messages.error(request, "This event has already occurred.")
            return redirect('event_detail', slug=event.slug)

        if event.is_full:
            messages.error(request, "This event is fully booked.")
            return redirect('event_detail', slug=event.slug)

        # Check if already registered
        reg, created = Registration.objects.get_or_create(event=event, user=request.user)
        
        if not created and reg.status == 'Confirmed':
            messages.warning(request, "You are already registered for this event.")
        else:
            reg.status = 'Confirmed'
            reg.save()
            messages.success(request, f"Successfully registered for {event.title}!")

        # Support AJAX check
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f"Registered successfully!"})

        return redirect('event_detail', slug=event.slug)

    return redirect('event_detail', slug=event.slug)

@login_required
def cancel_registration(request, slug):
    event = get_object_or_404(Event, slug=slug)

    if request.method == 'POST':
        reg = Registration.objects.filter(event=event, user=request.user).first()
        if reg:
            reg.delete() # Or set status='Cancelled'. Deleting is cleaner to let them re-register if needed.
            messages.success(request, f"Registration for {event.title} has been cancelled.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Registration cancelled successfully.'})
        else:
            messages.error(request, "You do not have an active registration for this event.")

        return redirect('dashboard')

    return redirect('dashboard')

@login_required
def dashboard(request):
    # Registered events
    registrations = Registration.objects.filter(user=request.user, status='Confirmed').select_related('event')
    
    # Organized events (if organizer)
    organized_events = Event.objects.filter(organizer=request.user).order_by('-created_at')

    context = {
        'registrations': registrations,
        'organized_events': organized_events,
    }
    return render(request, 'events/dashboard.html', context)

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, f"Event '{event.title}' created successfully!")
            return redirect('dashboard')
    else:
        form = EventForm()

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event'})

@login_required
def edit_event(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event '{event.title}' updated successfully!")
            return redirect('dashboard')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Edit Event', 'event': event})

@login_required
def delete_event(request, slug):
    event = get_object_or_404(Event, slug=slug, organizer=request.user)
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f"Event '{title}' deleted successfully.")
        return redirect('dashboard')
    return redirect('dashboard')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            login(request, user)
            messages.success(request, f"Welcome to Eventora, {user.first_name or user.username}!")
            return redirect('dashboard')
    else:
        form = SignUpForm()

    return render(request, 'events/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'events/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

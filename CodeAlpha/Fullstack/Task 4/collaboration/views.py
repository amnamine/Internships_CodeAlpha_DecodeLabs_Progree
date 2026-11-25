import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Room, SignalMessage, SharedFile, Profile

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            room_name = request.POST.get('room_name', 'Untitled Room')
            room = Room.objects.create(name=room_name, created_by=request.user)
            return redirect('room', room_code=room.code)
        elif action == 'join':
            room_code = request.POST.get('room_code', '').strip()
            try:
                room = Room.objects.get(code=room_code)
                return redirect('room', room_code=room.code)
            except Room.DoesNotExist:
                return render(request, 'dashboard.html', {
                    'error': 'Room code not found. Please check and try again.',
                    'rooms': Room.objects.filter(created_by=request.user).order_by('-created_at')
                })
    
    rooms = Room.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'rooms': rooms})

@login_required
def room_view(request, room_code):
    try:
        room = Room.objects.get(code=room_code)
    except Room.DoesNotExist:
        return redirect('dashboard')
    
    # Clean up very old signal messages for this room to prevent database bloat
    cutoff = timezone.now() - timezone.timedelta(minutes=5)
    SignalMessage.objects.filter(room_code=room_code, created_at__lt=cutoff).delete()
    
    # Get previously uploaded files
    files = room.files.all().order_by('-uploaded_at')
    
    context = {
        'room': room,
        'username': request.user.username,
        'user_color': request.user.profile.avatar_color,
        'files': files,
    }
    return render(request, 'room.html', context)

@login_required
@csrf_exempt
def send_signal(request, room_code):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            receiver = data.get('receiver', '')
            message_type = data.get('message_type', '')
            content = data.get('content', '')
            
            # Save the signal message
            SignalMessage.objects.create(
                room_code=room_code,
                sender=request.user.username,
                receiver=receiver,
                message_type=message_type,
                content=content
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@login_required
def get_signals(request, room_code):
    username = request.user.username
    # Get messages meant specifically for this user or broadcast to all
    # where the sender is not the requesting user themselves
    signals = SignalMessage.objects.filter(
        room_code=room_code
    ).filter(
        models.Q(receiver=username) | models.Q(receiver='all')
    ).exclude(
        sender=username
    ).order_by('created_at')
    
    # Build list of signals to return
    result = []
    for sig in signals:
        result.append({
            'sender': sig.sender,
            'receiver': sig.receiver,
            'message_type': sig.message_type,
            'content': sig.content,
            'timestamp': sig.created_at.isoformat()
        })
        
    # Delete the retrieved signals so they are only consumed once
    signals.delete()
    
    return JsonResponse({'signals': result})

@login_required
@csrf_exempt
def upload_file(request, room_code):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            room = Room.objects.get(code=room_code)
            uploaded = request.FILES['file']
            shared_file = SharedFile.objects.create(
                room=room,
                sender=request.user,
                file=uploaded,
                filename=uploaded.name
            )
            return JsonResponse({
                'status': 'success',
                'file_id': shared_file.id,
                'filename': shared_file.filename,
                'url': shared_file.file.url,
                'sender': shared_file.sender.username,
                'uploaded_at': shared_file.uploaded_at.strftime('%H:%M')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid file upload request'}, status=400)

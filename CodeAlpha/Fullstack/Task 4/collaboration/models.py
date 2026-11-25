import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_color = models.CharField(max_length=7, default='#7c3aed') # Default accent color
    status = models.CharField(max_length=100, default='Ready to collaborate')

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Give users a random cool avatar color
        import random
        colors = ['#7c3aed', '#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6']
        Profile.objects.create(user=instance, avatar_color=random.choice(colors))

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Room(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class SignalMessage(models.Model):
    room_code = models.CharField(max_length=50)
    sender = models.CharField(max_length=100) # username of sender
    receiver = models.CharField(max_length=100) # username of receiver
    message_type = models.CharField(max_length=20) # 'offer', 'answer', 'candidate'
    content = models.TextField() # JSON representation of the SDP/candidate
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Signal from {self.sender} to {self.receiver} [{self.message_type}]"

class SharedFile(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='files')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='shared_files/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} in {self.room.name}"

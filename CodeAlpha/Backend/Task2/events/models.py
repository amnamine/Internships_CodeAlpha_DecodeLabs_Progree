from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class, e.g. bi-laptop", default="bi-calendar-event")

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=250)
    capacity = models.PositiveIntegerField()
    image_url = models.URLField(max_length=500, blank=True, help_text="Unsplash or other image link. Leaves empty for category default.")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="events")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def registered_count(self):
        return self.registrations.filter(status='Confirmed').count()

    @property
    def occupancy_percentage(self):
        if self.capacity <= 0:
            return 100
        return min(100, int((self.registered_count / self.capacity) * 100))


    @property
    def available_spots(self):
        return max(0, self.capacity - self.registered_count)

    @property
    def is_full(self):
        return self.available_spots <= 0

    @property
    def is_past(self):
        event_datetime = timezone.make_aware(timezone.datetime.combine(self.date, self.time))
        return event_datetime < timezone.now()

    def __str__(self):
        return self.title

class Registration(models.Model):
    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)
    ticket_code = models.CharField(max_length=100, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')

    class Meta:
        unique_together = ('event', 'user')

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"

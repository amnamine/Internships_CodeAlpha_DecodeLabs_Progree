from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Event, Registration
from datetime import date, time

class EventSystemTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='tester', password='testpassword')
        self.organizer = User.objects.create_user(username='organizer', password='testpassword')
        
        # Create category
        self.category = Category.objects.create(name='Tech', slug='tech', icon='bi-laptop')
        
        # Create event
        self.event = Event.objects.create(
            title='AI Meetup',
            category=self.category,
            description='Let\'s discuss AI.',
            date=date.today(),
            time=time(18, 0),
            location='Online',
            capacity=2,
            organizer=self.organizer
        )

    def test_event_properties(self):
        # Assert properties on newly created event
        self.assertEqual(self.event.registered_count, 0)
        self.assertEqual(self.event.available_spots, 2)
        self.assertFalse(self.event.is_full)
        self.assertEqual(self.event.occupancy_percentage, 0)

    def test_registration_and_spots(self):
        # Register user
        reg = Registration.objects.create(event=self.event, user=self.user, status='Confirmed')
        
        self.assertEqual(self.event.registered_count, 1)
        self.assertEqual(self.event.available_spots, 1)
        self.assertFalse(self.event.is_full)
        self.assertEqual(self.event.occupancy_percentage, 50)
        
        # Register second user (organizer)
        reg2 = Registration.objects.create(event=self.event, user=self.organizer, status='Confirmed')
        
        self.assertEqual(self.event.registered_count, 2)
        self.assertEqual(self.event.available_spots, 0)
        self.assertTrue(self.event.is_full)
        self.assertEqual(self.event.occupancy_percentage, 100)

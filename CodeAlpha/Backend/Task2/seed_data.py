import os
import django
from datetime import datetime, date, time, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_manager.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import Category, Event, Registration

def seed():
    print("Seeding database...")
    
    # 1. Create Organizer / User
    organizer, created = User.objects.get_or_create(
        username='admin',
        email='admin@eventora.com',
        first_name='Amine',
        last_name='Organizer'
    )
    if created:
        organizer.set_password('admin123')
        organizer.is_superuser = True
        organizer.is_staff = True
        organizer.save()
        print("Created superuser 'admin' with password 'admin123'")
    else:
        print("Superuser 'admin' already exists")

    # 2. Create Categories
    categories_data = [
        {'name': 'Technology', 'slug': 'technology', 'icon': 'bi-laptop'},
        {'name': 'Music', 'slug': 'music', 'icon': 'bi-music-note-beamed'},
        {'name': 'Sports', 'slug': 'sports', 'icon': 'bi-trophy-fill'},
        {'name': 'Arts & Crafts', 'slug': 'arts', 'icon': 'bi-palette-fill'},
    ]

    categories = {}
    for cat_info in categories_data:
        cat, created = Category.objects.get_or_create(
            name=cat_info['name'],
            defaults={'slug': cat_info['slug'], 'icon': cat_info['icon']}
        )
        categories[cat_info['slug']] = cat
        if created:
            print(f"Created category '{cat.name}'")

    # 3. Create Events
    today = date.today()
    
    events_data = [
        {
            'title': 'Next-Gen AI & Machine Learning Summit',
            'category': categories['technology'],
            'description': 'Join leading experts from Google, DeepMind, and top tier AI companies for a full day of presentations on the future of agentic AI, LLMs, and neural networks. Network with founders and researchers.',
            'date': today + timedelta(days=30),
            'time': time(10, 0),
            'location': 'Silicon Valley Convention Center & Hybrid',
            'capacity': 150,
            'image_url': 'https://images.unsplash.com/photo-1591453089816-0fbb971b454c?auto=format&fit=crop&q=80&w=800'
        },
        {
            'title': 'Cyberpunk Synthwave Night: Resonance',
            'category': categories['music'],
            'description': 'Get ready for an immersive night filled with heavy synthesizer beats, retro-futuristic laser shows, and performances by code-synthesizers. Dress code: Cyberpunk/Neon.',
            'date': today + timedelta(days=12),
            'time': time(21, 0),
            'location': 'The Glass Dome Arena, Sector 4',
            'capacity': 250,
            'image_url': 'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&q=80&w=800'
        },
        {
            'title': 'Ultimate Esports Championship 2026',
            'category': categories['sports'],
            'description': 'Witness the world\'s top esports athletes face off in the final matches of the year. Grand prizes, interactive viewing lounges, and meet-and-greet sessions with pro teams.',
            'date': today + timedelta(days=18),
            'time': time(14, 30),
            'location': 'Hyperion Esports Stadium, Austin TX',
            'capacity': 80,
            'image_url': 'https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&q=80&w=800'
        },
        {
            'title': 'Modern Digital Art & NFTs Exhibition',
            'category': categories['arts'],
            'description': 'Explore high-fidelity digital art displays, interactive generative canvases, virtual reality sculpting booths, and discussions on ownership in the creator economy.',
            'date': today + timedelta(days=45),
            'time': time(11, 0),
            'location': 'Metropolitan Museum of Contemporary Art',
            'capacity': 45,
            'image_url': 'https://images.unsplash.com/photo-1561214115-f2f134cc4912?auto=format&fit=crop&q=80&w=800'
        }
    ]

    for ev_info in events_data:
        ev, created = Event.objects.get_or_create(
            title=ev_info['title'],
            defaults={
                'category': ev_info['category'],
                'description': ev_info['description'],
                'date': ev_info['date'],
                'time': ev_info['time'],
                'location': ev_info['location'],
                'capacity': ev_info['capacity'],
                'image_url': ev_info['image_url'],
                'organizer': organizer
            }
        )
        if created:
            print(f"Created event '{ev.title}'")

    # Add a dummy registration for testing
    # Register the admin for the AI Summit
    ai_summit = Event.objects.filter(slug__contains='ai-machine-learning').first()
    if ai_summit:
        reg, created = Registration.objects.get_or_create(
            event=ai_summit,
            user=organizer,
            defaults={'status': 'Confirmed'}
        )
        if created:
            print(f"Registered user '{organizer.username}' for '{ai_summit.title}'")

    print("Seeding completed successfully!")

if __name__ == '__main__':
    seed()

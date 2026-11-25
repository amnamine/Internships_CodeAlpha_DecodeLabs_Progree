import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from board.models import UserProfile, EmployerProfile, CandidateProfile, JobListing, JobApplication

class Command(BaseCommand):
    help = 'Seeds the database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        JobApplication.objects.all().delete()
        JobListing.objects.all().delete()
        CandidateProfile.objects.all().delete()
        EmployerProfile.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # 1. Create Superuser if not exists
        if not User.objects.filter(username='admin').exists():
            self.stdout.write('Creating superuser...')
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
            UserProfile.objects.get_or_create(user=admin_user, role='employer')
            EmployerProfile.objects.get_or_create(
                user=admin_user,
                company_name='Admin Corp',
                website='https://admincorp.com',
                description='The overall system administration company.',
                location='Global'
            )

        # 2. Create Employers
        employers_data = [
            {
                'username': 'google_emp', 'email': 'careers@google.com', 'pwd': 'password123',
                'company': 'Google', 'site': 'https://careers.google.com',
                'desc': 'Google is a global technology leader focusing on search, advertising, cloud, and AI.',
                'loc': 'Mountain View, CA / Remote'
            },
            {
                'username': 'stripe_emp', 'email': 'jobs@stripe.com', 'pwd': 'password123',
                'company': 'Stripe', 'site': 'https://stripe.com',
                'desc': 'Stripe is a financial infrastructure platform for the internet, powering millions of businesses.',
                'loc': 'San Francisco, CA / Remote'
            },
            {
                'username': 'netflix_emp', 'email': 'jobs@netflix.com', 'pwd': 'password123',
                'company': 'Netflix', 'site': 'https://netflix.com',
                'desc': 'Netflix is the world\'s leading streaming entertainment service with millions of paid memberships.',
                'loc': 'Los Gatos, CA'
            }
        ]

        employers = []
        for data in employers_data:
            user = User.objects.create_user(username=data['username'], email=data['email'], password=data['pwd'])
            UserProfile.objects.create(user=user, role='employer')
            EmployerProfile.objects.create(
                user=user,
                company_name=data['company'],
                website=data['site'],
                description=data['desc'],
                location=data['loc']
            )
            employers.append(user)
            self.stdout.write(f"Created Employer: {data['company']}")

        # 3. Create Candidates
        candidates_data = [
            {
                'username': 'john_doe', 'first': 'John', 'last': 'Doe', 'email': 'john.doe@example.com', 'pwd': 'password123',
                'bio': 'Passionate Full Stack Engineer with 4 years of experience building modern web apps.',
                'skills': 'Python, Django, JavaScript, React, PostgreSQL, CSS, HTML',
                'edu': 'B.S. in Computer Science - Stanford University',
                'exp': 'Frontend Engineer at TechCorp (2 years)\nSoftware Developer at DevShop (2 years)'
            },
            {
                'username': 'jane_smith', 'first': 'Jane', 'last': 'Smith', 'email': 'jane.smith@example.com', 'pwd': 'password123',
                'bio': 'UI/UX Developer and Designer focusing on accessible web interfaces and fluid CSS animations.',
                'skills': 'Figma, CSS3, HTML5, JavaScript, Vue.js, Django Templates',
                'edu': 'B.A. in Digital Media - NYU',
                'exp': 'UI Specialist at WebCreative (3 years)\nFreelance Web Designer (2 years)'
            }
        ]

        candidates = []
        for data in candidates_data:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['pwd'],
                first_name=data['first'],
                last_name=data['last']
            )
            UserProfile.objects.create(user=user, role='candidate')
            CandidateProfile.objects.create(
                user=user,
                bio=data['bio'],
                skills=data['skills'],
                education=data['edu'],
                experience=data['exp']
            )
            candidates.append(user)
            self.stdout.write(f"Created Candidate: {data['first']} {data['last']}")

        # 4. Create Job Listings
        jobs_data = [
            {
                'employer': employers[0],
                'title': 'Senior Python/Django Engineer',
                'description': 'We are looking for a Senior Django Engineer to join our cloud platform team. You will build high-scale, robust web APIs, integrate with microservices, and optimize query performances.',
                'requirements': '5+ years of experience with Python & Django\nStrong knowledge of REST APIs and PostgreSQL\nFamiliarity with containerization (Docker, Kubernetes)\nGreat communication and system design skills',
                'location': 'Remote (US/Canada)',
                'salary': '$130,000 - $160,000',
                'type': 'remote',
                'category': 'Backend Development'
            },
            {
                'employer': employers[0],
                'title': 'Frontend UX Engineer',
                'description': 'Join our design systems team to shape the future of our web interfaces. You will translate designs to beautiful, semantic, highly performant code and implement gorgeous CSS micro-interactions.',
                'requirements': 'Strong expertise in HTML5, CSS3 (Grid, Flexbox, Animations)\nProficiency in Vanilla JS and modern JS frameworks\nExperience with responsive design and accessibility (WCAG)\nEye for clean visual layouts and smooth transitions',
                'location': 'Mountain View, CA',
                'salary': '$110,000 - $140,000',
                'type': 'full_time',
                'category': 'Frontend Development'
            },
            {
                'employer': employers[1],
                'title': 'Full Stack Developer (React & Django)',
                'description': 'Stripe is looking for a generalist Full Stack Developer to help build features for merchant dashboards. You will work on both the backend models/APIs in Django and interactive dashboard components in React.',
                'requirements': 'Proficient in Python and JavaScript\nExperience with React and Django framework\nUnderstanding of database design and SQL optimization\nExcellent problem-solving abilities',
                'location': 'Remote / San Francisco',
                'salary': '$120,000 - $150,000',
                'type': 'full_time',
                'category': 'Full Stack Development'
            },
            {
                'employer': employers[2],
                'title': 'Intern Software Engineer (Backend)',
                'description': 'Netflix is offering a 6-month internship in our backend engineering group. You will gain hands-on experience working on real production APIs, shadowing senior developers, and writing robust tests.',
                'requirements': 'Currently pursuing a degree in CS or related technical field\nBasic knowledge of Python, Java, or Go\nUnderstanding of web protocols and algorithms\nEagerness to learn and collaborate',
                'location': 'Los Gatos, CA',
                'salary': '$45 - $60 / hour',
                'type': 'internship',
                'category': 'Backend Development'
            }
        ]

        jobs = []
        for data in jobs_data:
            job = JobListing.objects.create(
                employer=data['employer'],
                title=data['title'],
                description=data['description'],
                requirements=data['requirements'],
                location=data['location'],
                salary_range=data['salary'],
                job_type=data['type'],
                category=data['category']
            )
            jobs.append(job)
            self.stdout.write(f"Created Job: {data['title']}")

        # 5. Create Applications
        JobApplication.objects.create(
            job=jobs[0],
            candidate=candidates[0],
            cover_letter="I am extremely excited about the Senior Python/Django Engineer role. With 4+ years of Python experience, I am confident in my ability to hit the ground running.",
            status='pending'
        )
        JobApplication.objects.create(
            job=jobs[2],
            candidate=candidates[0],
            cover_letter="I love Stripe's product and developer-first approach. I have built multiple projects integrating Stripe payments and django apps.",
            status='shortlisted'
        )
        JobApplication.objects.create(
            job=jobs[1],
            candidate=candidates[1],
            cover_letter="My profile is a great match for the Frontend UX Engineer role. I love crafting pixel-perfect, accessible, and highly aesthetic interfaces.",
            status='reviewing'
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))

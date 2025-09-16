import random
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import User


class Command(BaseCommand):
    help = 'Creates test users for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(self.style.SUCCESS(f'Creating {count} test users...'))

        # Sample first and last names
        first_names = [
            'John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert',
            'Jennifer', 'William', 'Elizabeth', 'James', 'Olivia', 'Daniel',
            'Sophia', 'Matthew', 'Emma', 'Christopher', 'Ava', 'Andrew', 'Mia'
        ]
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller',
            'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White',
            'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson'
        ]

        # Create users in a transaction
        with transaction.atomic():
            created_count = 0
            for i in range(count):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
                email = f"{username}@example.com"
                
                # Create user if it doesn't exist
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='testpassword',
                        first_name=first_name,
                        last_name=last_name
                    )
                    created_count += 1
                    self.stdout.write(f"Created user: {user.username} ({user.email})")
                else:
                    self.stdout.write(f"User with email {email} already exists, skipping...")
            
            # Always create a superuser for admin access if it doesn't exist
            admin_email = 'admin@example.com'
            if not User.objects.filter(email=admin_email).exists():
                User.objects.create_superuser(
                    username='admin',
                    email=admin_email,
                    password='testpassword',
                    first_name='Admin',
                    last_name='User'
                )
                created_count += 1
                self.stdout.write("Created superuser: admin (admin@example.com)")
            else:
                self.stdout.write("Superuser admin@example.com already exists, skipping...")

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} test users'))
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import CustomUser, Follow


class Command(BaseCommand):
    help = 'Creates test follows between users for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-follows',
            type=int,
            default=1,
            help='Minimum number of follows per user (default: 1)'
        )
        parser.add_argument(
            '--max-follows',
            type=int,
            default=5,
            help='Maximum number of follows per user (default: 5)'
        )

    def handle(self, *args, **options):
        min_follows = options['min_follows']
        max_follows = options['max_follows']
        
        self.stdout.write(self.style.SUCCESS(f'Creating test follows (min: {min_follows}, max: {max_follows} per user)...'))

        # Get all users
        users = list(CustomUser.objects.all())
        
        if len(users) < 2:
            self.stdout.write(self.style.ERROR('Not enough users to create follows. Please run create_test_users first.'))
            return

        # Create follows in a transaction
        with transaction.atomic():
            created_count = 0
            
            for user in users:
                # Determine how many users this user will follow
                num_follows = random.randint(min_follows, min(max_follows, len(users) - 1))
                
                # Get potential users to follow (excluding self)
                potential_follows = [u for u in users if u.id != user.id]
                
                # Randomly select users to follow
                users_to_follow = random.sample(potential_follows, min(num_follows, len(potential_follows)))
                
                for author in users_to_follow:
                    # Create follow if it doesn't exist
                    follow, created = Follow.objects.get_or_create(
                        user=user,
                        author=author
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f"Created follow: {user.username} -> {author.username}")
                    else:
                        self.stdout.write(f"Follow {user.username} -> {author.username} already exists, skipping...")

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} test follows'))
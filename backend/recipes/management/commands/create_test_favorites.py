import random
from django.core.management.base import BaseCommand
from django.db import transaction
from recipes.models import Recipe, Favorite
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Creates test favorite recipes for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-favorites',
            type=int,
            default=1,
            help='Minimum number of favorites per user (default: 1)'
        )
        parser.add_argument(
            '--max-favorites',
            type=int,
            default=5,
            help='Maximum number of favorites per user (default: 5)'
        )

    def handle(self, *args, **options):
        min_favorites = options['min_favorites']
        max_favorites = options['max_favorites']
        
        self.stdout.write(self.style.SUCCESS(f'Creating test favorites (min: {min_favorites}, max: {max_favorites} per user)...'))

        # Get all users and recipes
        users = list(CustomUser.objects.all())
        recipes = list(Recipe.objects.all())
        
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please run create_test_users first.'))
            return
        
        if not recipes:
            self.stdout.write(self.style.ERROR('No recipes found. Please run create_test_recipes first.'))
            return

        # Create favorites in a transaction
        with transaction.atomic():
            created_count = 0
            
            for user in users:
                # Determine how many recipes this user will favorite
                num_favorites = random.randint(min_favorites, min(max_favorites, len(recipes)))
                
                # Randomly select recipes to favorite
                recipes_to_favorite = random.sample(recipes, num_favorites)
                
                for recipe in recipes_to_favorite:
                    # Create favorite if it doesn't exist
                    favorite, created = Favorite.objects.get_or_create(
                        user=user,
                        recipe=recipe
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f"Created favorite: {user.username} -> {recipe.name}")
                    else:
                        self.stdout.write(f"Favorite {user.username} -> {recipe.name} already exists, skipping...")

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} test favorites'))
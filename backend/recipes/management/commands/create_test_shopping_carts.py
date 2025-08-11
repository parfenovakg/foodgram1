import random
from django.core.management.base import BaseCommand
from django.db import transaction
from recipes.models import Recipe, ShoppingCart
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Creates test shopping cart items for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-items',
            type=int,
            default=1,
            help='Minimum number of items in shopping cart per user (default: 1)'
        )
        parser.add_argument(
            '--max-items',
            type=int,
            default=3,
            help='Maximum number of items in shopping cart per user (default: 3)'
        )

    def handle(self, *args, **options):
        min_items = options['min_items']
        max_items = options['max_items']
        
        self.stdout.write(self.style.SUCCESS(f'Creating test shopping cart items (min: {min_items}, max: {max_items} per user)...'))

        # Get all users and recipes
        users = list(CustomUser.objects.all())
        recipes = list(Recipe.objects.all())
        
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please run create_test_users first.'))
            return
        
        if not recipes:
            self.stdout.write(self.style.ERROR('No recipes found. Please run create_test_recipes first.'))
            return

        # Create shopping cart items in a transaction
        with transaction.atomic():
            created_count = 0
            
            for user in users:
                # Determine how many recipes this user will add to shopping cart
                num_items = random.randint(min_items, min(max_items, len(recipes)))
                
                # Randomly select recipes to add to shopping cart
                recipes_to_add = random.sample(recipes, num_items)
                
                for recipe in recipes_to_add:
                    # Create shopping cart item if it doesn't exist
                    cart_item, created = ShoppingCart.objects.get_or_create(
                        user=user,
                        recipe=recipe
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f"Added to shopping cart: {user.username} -> {recipe.name}")
                    else:
                        self.stdout.write(f"Shopping cart item {user.username} -> {recipe.name} already exists, skipping...")

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} test shopping cart items'))
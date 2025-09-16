import random
import os
import base64
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files.base import ContentFile
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Creates test recipes for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of recipes to create (default: 20)'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(self.style.SUCCESS(f'Creating {count} test recipes...'))

        # Check if we have users, tags, and ingredients
        users = list(CustomUser.objects.all())
        tags = list(Tag.objects.all())
        ingredients = list(Ingredient.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please run create_test_users first.'))
            return
        
        if not tags:
            self.stdout.write(self.style.ERROR('No tags found. Please run create_test_tags first.'))
            return
        
        if not ingredients:
            self.stdout.write(self.style.ERROR('No ingredients found. Please run create_test_ingredients first.'))
            return

        # Sample recipe names and descriptions
        recipe_names = [
            'Delicious Pasta', 'Homemade Pizza', 'Vegetable Stir Fry', 'Chocolate Cake',
            'Chicken Curry', 'Beef Stew', 'Vegetarian Lasagna', 'Fruit Salad',
            'Grilled Salmon', 'Mushroom Risotto', 'Tomato Soup', 'Caesar Salad',
            'Pancakes', 'Omelette', 'Roast Chicken', 'Beef Burger',
            'Vegetable Soup', 'Apple Pie', 'Cheesecake', 'Sushi Rolls',
            'Tacos', 'Guacamole', 'Hummus', 'Falafel Wrap',
            'Pad Thai', 'Butter Chicken', 'Tiramisu', 'Carrot Cake',
            'Mashed Potatoes', 'Roasted Vegetables'
        ]

        # Sample recipe descriptions
        descriptions = [
            'A delicious and easy recipe that everyone will love.',
            'Perfect for a family dinner or special occasion.',
            'Quick and healthy meal that can be prepared in under 30 minutes.',
            'Traditional recipe with a modern twist.',
            'Comfort food at its best, warming and satisfying.',
            'Light and refreshing, ideal for summer days.',
            'Rich and indulgent, a real treat for dessert lovers.',
            'Nutritious and filling, packed with protein and vegetables.',
            'Simple ingredients combined to create amazing flavors.',
            'An impressive dish that looks like it took hours to prepare.'
        ]

        # Create a simple placeholder image (1x1 pixel) for test recipes
        # In a real scenario, you would use actual food images
        placeholder_image_data = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
        
        # Create recipes in a transaction
        with transaction.atomic():
            created_count = 0
            for i in range(count):
                # Select random data for the recipe
                name = random.choice(recipe_names)
                author = random.choice(users)
                text = random.choice(descriptions)
                cooking_time = random.randint(10, 120)  # 10 minutes to 2 hours
                
                # Create recipe
                recipe = Recipe(
                    author=author,
                    name=f"{name} #{i+1}",
                    # short_code=f"#{i+1}",
                    text=text,
                    cooking_time=cooking_time,
                )

                # Add image
                image_data = base64.b64decode(placeholder_image_data)
                recipe.image.save(f'recipe_{i+1}.png', ContentFile(image_data), save=False)
                
                recipe.save()
                
                # Add random tags (1-3 tags per recipe)
                recipe_tags = random.sample(tags, random.randint(1, min(3, len(tags))))
                recipe.tags.set(recipe_tags)
                
                # Add random ingredients (3-8 ingredients per recipe)
                recipe_ingredients = random.sample(ingredients, random.randint(3, min(8, len(ingredients))))
                for ingredient in recipe_ingredients:
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=random.randint(1, 500)  # Random amount between 1 and 500
                    )
                
                created_count += 1
                self.stdout.write(f"Created recipe: {recipe.name} by {recipe.author.username}")

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} test recipes'))
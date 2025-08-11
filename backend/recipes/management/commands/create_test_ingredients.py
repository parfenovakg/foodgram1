from django.core.management.base import BaseCommand
from django.db import transaction
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Creates test ingredients for development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test ingredients...'))

        # Define common ingredients with their measurement units
        ingredients_data = [
            {'name': 'Salt', 'measurement_unit': 'g'},
            {'name': 'Sugar', 'measurement_unit': 'g'},
            {'name': 'Flour', 'measurement_unit': 'g'},
            {'name': 'Butter', 'measurement_unit': 'g'},
            {'name': 'Milk', 'measurement_unit': 'ml'},
            {'name': 'Eggs', 'measurement_unit': 'pcs'},
            {'name': 'Olive oil', 'measurement_unit': 'ml'},
            {'name': 'Onion', 'measurement_unit': 'pcs'},
            {'name': 'Garlic', 'measurement_unit': 'cloves'},
            {'name': 'Tomatoes', 'measurement_unit': 'pcs'},
            {'name': 'Chicken breast', 'measurement_unit': 'g'},
            {'name': 'Beef', 'measurement_unit': 'g'},
            {'name': 'Rice', 'measurement_unit': 'g'},
            {'name': 'Pasta', 'measurement_unit': 'g'},
            {'name': 'Potatoes', 'measurement_unit': 'pcs'},
            {'name': 'Carrots', 'measurement_unit': 'pcs'},
            {'name': 'Bell peppers', 'measurement_unit': 'pcs'},
            {'name': 'Cheese', 'measurement_unit': 'g'},
            {'name': 'Yogurt', 'measurement_unit': 'g'},
            {'name': 'Honey', 'measurement_unit': 'ml'},
            {'name': 'Lemon', 'measurement_unit': 'pcs'},
            {'name': 'Lime', 'measurement_unit': 'pcs'},
            {'name': 'Cilantro', 'measurement_unit': 'g'},
            {'name': 'Parsley', 'measurement_unit': 'g'},
            {'name': 'Basil', 'measurement_unit': 'g'},
            {'name': 'Thyme', 'measurement_unit': 'g'},
            {'name': 'Rosemary', 'measurement_unit': 'g'},
            {'name': 'Cinnamon', 'measurement_unit': 'g'},
            {'name': 'Cumin', 'measurement_unit': 'g'},
            {'name': 'Paprika', 'measurement_unit': 'g'},
            {'name': 'Chili powder', 'measurement_unit': 'g'},
            {'name': 'Black pepper', 'measurement_unit': 'g'},
            {'name': 'Soy sauce', 'measurement_unit': 'ml'},
            {'name': 'Vinegar', 'measurement_unit': 'ml'},
            {'name': 'Mustard', 'measurement_unit': 'g'},
            {'name': 'Ketchup', 'measurement_unit': 'g'},
            {'name': 'Mayonnaise', 'measurement_unit': 'g'},
            {'name': 'Cream', 'measurement_unit': 'ml'},
            {'name': 'Coconut milk', 'measurement_unit': 'ml'},
            {'name': 'Chocolate', 'measurement_unit': 'g'},
            {'name': 'Vanilla extract', 'measurement_unit': 'ml'},
            {'name': 'Baking powder', 'measurement_unit': 'g'},
            {'name': 'Baking soda', 'measurement_unit': 'g'},
            {'name': 'Yeast', 'measurement_unit': 'g'},
            {'name': 'Bread crumbs', 'measurement_unit': 'g'},
            {'name': 'Nuts', 'measurement_unit': 'g'},
            {'name': 'Raisins', 'measurement_unit': 'g'},
            {'name': 'Oats', 'measurement_unit': 'g'},
            {'name': 'Maple syrup', 'measurement_unit': 'ml'},
            {'name': 'Brown sugar', 'measurement_unit': 'g'},
        ]

        # Create ingredients in a transaction
        with transaction.atomic():
            created_count = 0
            for ingredient_data in ingredients_data:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_data['name'],
                    measurement_unit=ingredient_data['measurement_unit']
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"Created ingredient: {ingredient.name} ({ingredient.measurement_unit})")
                else:
                    self.stdout.write(f"Ingredient {ingredient.name} already exists, skipping...")

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} test ingredients'))
from django.core.management.base import BaseCommand
from django.db import transaction
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Creates test tags for development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating test tags...'))

        # Define common recipe tags with their colors
        tags_data = [
            {'name': 'Breakfast', 'color': '#E26CFF', 'slug': 'breakfast'},
            {'name': 'Lunch', 'color': '#49B64E', 'slug': 'lunch'},
            {'name': 'Dinner', 'color': '#8775D2', 'slug': 'dinner'},
            {'name': 'Dessert', 'color': '#FF4A4A', 'slug': 'dessert'},
            {'name': 'Vegetarian', 'color': '#7ED321', 'slug': 'vegetarian'},
            {'name': 'Vegan', 'color': '#4A90E2', 'slug': 'vegan'},
            {'name': 'Gluten-free', 'color': '#F5A623', 'slug': 'gluten-free'},
            {'name': 'Dairy-free', 'color': '#9B9B9B', 'slug': 'dairy-free'},
            {'name': 'Low-carb', 'color': '#50E3C2', 'slug': 'low-carb'},
            {'name': 'Quick', 'color': '#FF5E5E', 'slug': 'quick'}
        ]

        # Create tags in a transaction
        with transaction.atomic():
            created_count = 0
            for tag_data in tags_data:
                tag, created = Tag.objects.get_or_create(
                    slug=tag_data['slug'],
                    defaults={
                        'name': tag_data['name'],
                        'color': tag_data['color']
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"Created tag: {tag.name} ({tag.color})")
                else:
                    self.stdout.write(f"Tag {tag.name} already exists, skipping...")

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} test tags'))
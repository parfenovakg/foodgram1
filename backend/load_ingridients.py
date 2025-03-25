import os
import django

# Указываем Django, где находятся настройки проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")
django.setup()

import json
from recipes.models import Ingredient
from django.db import transaction

with open('../data/ingredients.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    with transaction.atomic():
        for item in data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=item['name'],
                defaults={'measurement_unit': item['measurement_unit']}
            )
            if created:
                print(f'Ингредиент {item["name"]} был создан')
            else:
                print(f'Ингредиент {item["name"]} уже существует')

print('Ингредиенты загружены!')

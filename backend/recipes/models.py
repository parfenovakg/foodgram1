from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True)
    measurement_unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, unique=True)  # HEX-код
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="recipes/")
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through="RecipeIngredient")
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('recipe', 'ingredient')

class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorited_by"
    )

    class Meta:
        unique_together = ('user', 'recipe')

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shopping_cart"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="in_shopping_cart"
    )

    class Meta:
        unique_together = ('user', 'recipe')

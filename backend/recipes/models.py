from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(max_length=255, unique=True)
    measurement_unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"

class Tag(models.Model):
    """Модель тегов для рецептов."""
    name = models.CharField(max_length=255, unique=True)
    color = models.CharField(max_length=7, default='#FFFFFF')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    """Связь между рецептами и ингредиентами с указанием количества."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name}: {self.amount}"

class Favorite(models.Model):
    """Модель для избранных рецептов."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="favorites")

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"

class ShoppingCart(models.Model):
    """Модель для списка покупок."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shopping_cart")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="shopping_cart")

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"

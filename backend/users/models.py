from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(CustomUser, related_name='follows', on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'author')
        indexes = [models.Index(fields=['user', 'author'])]

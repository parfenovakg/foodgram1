from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username

class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="following"
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        unique_together = ('user', 'author')

    def __str__(self):
        return f"{self.user} подписан на {self.author}"

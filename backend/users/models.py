from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.const import MAX_LENGTH_NAME


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=MAX_LENGTH_NAME)
    last_name = models.CharField(max_length=MAX_LENGTH_NAME)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follows',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'author'])
        ]

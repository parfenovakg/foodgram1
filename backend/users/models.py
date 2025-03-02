from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    username = models.CharField(max_length=150, unique=True, verbose_name="Никнейм")
    email = models.EmailField(unique=True, verbose_name="Адрес электронной почты")
    password = models.CharField(max_length=128, verbose_name="Пароль")
    avatar = models.ImageField(
        upload_to="avatars/",
        default="avatars/default.png",
        verbose_name="Аватар"
    )
    subscriptions = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="subscribers",
        blank=True,
        verbose_name="Подписки"
    )

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions_set",
        blank=True
    )

    def __str__(self):
        return self.username


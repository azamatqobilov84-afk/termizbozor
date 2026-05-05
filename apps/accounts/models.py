from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        MODERATOR = 'moderator', 'Moderator'
        VIEWER = 'viewer', 'Foydalanuvchi'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        verbose_name='Roli'
    )
    phone = models.CharField(
        max_length=20, blank=True, verbose_name='Telefon raqami'
    )
    preferred_market = models.ForeignKey(
        'markets.Market',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='preferred_by',
        verbose_name='Sevimli bozor'
    )

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return self.get_full_name() or self.username

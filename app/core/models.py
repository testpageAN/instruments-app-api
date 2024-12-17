"""
Database models.
"""
from django.conf import settings
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Instrument(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    tag = models.CharField(max_length=255)
    unit = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    type = models.CharField(max_length=30)
    manufacturer = models.CharField(max_length=100)
    serial_no = models.CharField(max_length=30)
    interval = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField()
    notes = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.tag

    @property
    def next_check(self):
        """Υπολογίζει την ημερομηνία για το επόμενο check."""
        return self.last_checked + timedelta(days=self.interval)

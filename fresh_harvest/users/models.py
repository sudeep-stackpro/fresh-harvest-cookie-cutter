from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom user manager where email_or_phone is the unique identifier
    instead of username.
    """

    def create_user(self, email_or_phone, name, password=None, **extra_fields):
        if not email_or_phone:
            raise ValueError("The email_or_phone field must be set")

        email_or_phone = self.normalize_email(email_or_phone)
        user = self.model(email_or_phone=email_or_phone, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email_or_phone, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email_or_phone, name, password, **extra_fields)


class User(AbstractUser):
    """
    Default custom user model for Fresh Harvest.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    # name = CharField(_("Name of User"), blank=True, max_length=255)
    # first_name = None  # type: ignore[assignment]
    # last_name = None  # type: ignore[assignment]

    # def get_absolute_url(self) -> str:
    #     """Get URL for user's detail view.

    #     Returns:
    #         str: URL for user detail.

    #     """
    #     return reverse("users:detail", kwargs={"username": self.username})
    first_name = None
    last_name = None

    name = models.CharField(max_length=100)
    email_or_phone = models.CharField(max_length=100, unique=True)
    location = models.TextField(blank=True, null=True)
    image = models.FileField(
        upload_to="user_images/",
        blank=True,
        null=True,
        default="user_images/default.png",
    )

    USERNAME_FIELD = "email_or_phone"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email_or_phone
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email_or_phone

from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


# @admin.register(User)
# class UserAdmin(auth_admin.UserAdmin):
#     form = UserAdminChangeForm
#     add_form = UserAdminCreationForm
#     fieldsets = (
#         (None, {"fields": ("username", "password")}),
#         (_("Personal info"), {"fields": ("name", "email")}),
#         (
#             _("Permissions"),
#             {
#                 "fields": (
#                     "is_active",
#                     "is_staff",
#                     "is_superuser",
#                     "groups",
#                     "user_permissions",
#                 ),
#             },
#         ),
#         (_("Important dates"), {"fields": ("last_login", "date_joined")}),
#     )
#     list_display = ["username", "name", "is_superuser"]
#     search_fields = ["name"]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    """Define admin model for custom User model with no username field."""

    # What will be shown in list view
    list_display = ("email_or_phone", "name", "is_staff", "is_superuser")
    search_fields = ("email_or_phone", "name")
    ordering = ("email_or_phone",)

    # Use email_or_phone instead of username
    fieldsets = (
        (None, {"fields": ("email_or_phone", "password")}),
        (_("Personal info"), {"fields": ("name", "location", "image")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email_or_phone", "name", "password1", "password2"),
            },
        ),
    )

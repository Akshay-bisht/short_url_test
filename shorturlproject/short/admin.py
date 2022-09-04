from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from short import models

# Register your models here.
@admin.register(models.MyUser)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('email', 'first_name', 'last_name', 'age', 'birth_date', 'solution_provider','otp_verified')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined',)
        }),
    )
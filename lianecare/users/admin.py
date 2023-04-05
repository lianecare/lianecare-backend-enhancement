from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from lianecare.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        auth_admin.UserAdmin.fieldsets
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'type'),
        }),
    )
    list_display = ["username", "email", "first_name", "last_name", "type", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]

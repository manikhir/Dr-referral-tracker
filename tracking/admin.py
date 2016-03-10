from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.

from .models import *

admin.site.register(Organization)
admin.site.register(Agent)
admin.site.register(PatientVisit)
admin.site.register(ThankyouMails)
admin.site.register(EmailReport)

def user_activate(modeladmin, request, queryset):
    queryset.update(is_active=True)
user_activate.short_description = "Activate user"


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    actions = [user_activate]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
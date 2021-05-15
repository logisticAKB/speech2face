from django.contrib import admin
from .models import UserTask


class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task_id',)


admin.site.register(UserTask, UserTaskAdmin)

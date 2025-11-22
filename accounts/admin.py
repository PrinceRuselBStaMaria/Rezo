from django.contrib import admin
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'email', 'role', 'department', 'is_active')
    list_filter = ('role', 'is_active', 'department')
    search_fields = ('first_name', 'last_name', 'email', 'employee_id')
    ordering = ('employee_id',)

from django.contrib import admin
from .models import Category, Asset, BorrowRecord, Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'first_name', 'last_name', 'role', 'department', 'email', 'is_active']
    list_filter = ['role', 'department', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    fields = ['first_name', 'last_name', 'email', 'role', 'department', 'phone', 'employee_id', 'password', 'is_active']

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'status', 'category')
    search_fields = ('name', 'serial_number')
    list_filter = ('status', 'category')

admin.site.register(Category)
admin.site.register(BorrowRecord)
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Asset, BorrowRecord, Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'first_name', 'last_name', 'role', 'department', 'email', 'is_active']
    list_filter = ['role', 'department', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    fields = ['first_name', 'last_name', 'email', 'role', 'department', 'phone', 'employee_id', 'password', 'is_active']

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'

admin.site.register(Category)
admin.site.register(BorrowRecord)
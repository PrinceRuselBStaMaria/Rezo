from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Asset, BorrowRecord

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
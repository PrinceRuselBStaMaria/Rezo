from django.contrib import admin
from .models import Category, Asset, BorrowRecord

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'status', 'category') # [cite: 394]
    search_fields = ('name', 'serial_number') # [cite: 395]
    list_filter = ('status', 'category')

admin.site.register(Category)
admin.site.register(BorrowRecord)
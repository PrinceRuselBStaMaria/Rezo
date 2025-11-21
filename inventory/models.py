from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Asset(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BORROWED', 'Borrowed'),
        ('REPAIR', 'Under Repair'),
        ('DISPOSED', 'Disposed'),
    ]
    name = models.CharField(max_length=100) # [cite: 360]
    serial_number = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    total_quantity = models.IntegerField(default=10)  # Total stock available (limit)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})" # [cite: 365]
    
    def get_borrowed_quantity(self):
        """Get total quantity currently borrowed"""
        return BorrowRecord.objects.filter(
            asset=self,
            is_returned=False
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
    
    def get_available_quantity(self):
        """Get available quantity for borrowing"""
        return self.total_quantity - self.get_borrowed_quantity()
    
    def is_stock_available(self):
        """Check if any stock is available"""
        return self.get_available_quantity() > 0

class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)  # Number of items borrowed
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.asset.name} (Qty: {self.quantity})"
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
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    total_quantity = models.IntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    image = models.ImageField(upload_to='media/assets/upload', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})"
    
    def get_borrowed_quantity(self):
        """Get total quantity currently borrowed (APPROVED and NOT returned only)"""
        borrowed = BorrowRecord.objects.filter(
            asset=self,
            is_returned=False,
            status='APPROVED'  # Only count APPROVED borrows
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        print(f"DEBUG: Asset {self.name} - Borrowed (Approved): {borrowed}")
        return borrowed
    
    def get_pending_quantity(self):
        """Get total quantity in pending requests"""
        pending = BorrowRecord.objects.filter(
            asset=self,
            is_returned=False,  # Add this to exclude returned requests
            status='PENDING'
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        print(f"DEBUG: Asset {self.name} - Pending: {pending}")
        return pending
    
    def get_available_quantity(self):
        """Get available quantity for borrowing (excluding pending requests)"""
        available = self.total_quantity - self.get_borrowed_quantity() - self.get_pending_quantity()
        print(f"DEBUG: Asset {self.name} - Total: {self.total_quantity}, Available: {available}")
        return available
    
    def is_stock_available(self):
        """Check if any stock is available"""
        return self.get_available_quantity() > 0

class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    borrow_date = models.DateField(auto_now_add=True)
    approved_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_borrows')
    rejection_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.asset.name} ({self.status})"
from django.db import models
from django.contrib.auth.models import User
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): 
        return self.name

class Asset(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BORROWED', 'Borrowed'),
        ('REPAIR', 'Under Repair'),
        ('DISPOSED', 'Disposed'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50, unique=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    total_quantity = models.IntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    image = models.ImageField(upload_to='media/assets/upload', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = f"AST-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})"
    
    def get_borrowed_quantity(self):
        """Get total quantity currently borrowed (APPROVED and NOT returned only)"""
        borrowed = BorrowRecord.objects.filter(
            asset=self,
            is_returned=False,
            status='APPROVED'
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        return borrowed
    
    def get_pending_quantity(self):
        """Get total quantity in PENDING requests (for staff view only)"""
        pending = BorrowRecord.objects.filter(
            asset=self,
            status='PENDING'
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        return pending
    
    def get_available_quantity(self):
        """Get available quantity for borrowing (only deduct APPROVED borrows, not PENDING)"""
        available = self.total_quantity - self.get_borrowed_quantity()
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
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='borrow_records')
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    borrow_date = models.DateField(auto_now_add=True)
    approved_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_borrow_records')
    rejection_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.asset.name} ({self.status})"
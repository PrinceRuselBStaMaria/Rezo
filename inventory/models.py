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

class DisposalRecord(models.Model):
    DISPOSAL_REASON_CHOICES = [
        ('DAMAGED', 'Damaged Beyond Repair'),
        ('OBSOLETE', 'Obsolete'),
        ('END_OF_LIFE', 'End of Life'),
        ('LOST', 'Lost/Missing'),
        ('OTHER', 'Other'),
    ]
    
    id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='disposal_records')
    quantity = models.IntegerField(default=1)
    reason = models.CharField(max_length=50, choices=DISPOSAL_REASON_CHOICES)
    description = models.TextField(blank=True, null=True)
    disposal_date = models.DateField(auto_now_add=True)
    disposed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='disposal_records')
    
    def __str__(self):
        return f"Disposal of {self.asset.name} - {self.quantity} units"
    
    def can_dispose(self):
        """Check if disposal quantity doesn't exceed available quantity"""
        available = self.asset.get_available_quantity()
        return self.quantity <= available

class MaintenanceRecord(models.Model):
    MAINTENANCE_TYPE_CHOICES = [
        ('PREVENTIVE', 'Preventive Maintenance'),
        ('CORRECTIVE', 'Corrective Maintenance'),
        ('EMERGENCY', 'Emergency Repair'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_requests')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance')
    request_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-request_date']
    
    def __str__(self):
        return f"{self.asset.name} - {self.get_maintenance_type_display()} ({self.status})"
    
    def is_overdue(self):
        """Check if maintenance is overdue (pending for more than 7 days)"""
        from datetime import timedelta
        if self.status == 'PENDING':
            days_pending = (timezone.now().date() - self.request_date).days
            return days_pending > 7
        return False
    
    def duration_days(self):
        """Calculate maintenance duration"""
        if self.completion_date and self.start_date:
            return (self.completion_date - self.start_date).days
        elif self.start_date:
            return (timezone.now().date() - self.start_date).days
        return 0
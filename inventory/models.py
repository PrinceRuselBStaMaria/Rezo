from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    total_quantity = models.IntegerField(default=10)  # Total stock available (limit)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    image = models.ImageField(upload_to='media/assets/upload', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})"
    
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

# Staff model - independent, creates its own User
class Staff(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('STAFF', 'Staff'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STAFF')
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    employee_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128, blank=True)  # Password for Django User
    date_joined = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Staff"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.role}"
    
    def is_admin(self):
        return self.role == 'ADMIN'
    
    def is_staff_member(self):
        return self.role == 'STAFF'

# When Staff is created, automatically create a Django User
@receiver(post_save, sender=Staff)
def create_user_for_staff(sender, instance, created, **kwargs):
    if created and instance.password:
        # Create username from email
        username = instance.email.split('@')[0]
        
        # Create new Django User with password
        user = User.objects.create_user(
            username=username,
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            password=instance.password,
            is_staff=(instance.role == 'ADMIN'),
            is_superuser=(instance.role == 'ADMIN')
        )

@receiver(post_save, sender=Staff)
def update_user_for_staff(sender, instance, **kwargs):
    try:
        user = User.objects.get(email=instance.email)
        user.first_name = instance.first_name
        user.last_name = instance.last_name
        user.is_staff = (instance.role == 'ADMIN')
        user.is_superuser = (instance.role == 'ADMIN')
        if instance.password and not user.check_password(instance.password):
            user.set_password(instance.password)
        user.save()
    except User.DoesNotExist:
        pass
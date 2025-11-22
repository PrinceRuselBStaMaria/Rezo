from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    # Prevent recursion
    if hasattr(instance, '_signal_processing'):
        return
    
    instance._signal_processing = True
    
    try:
        if created:
            # Create unique username from employee_id
            username = instance.employee_id
            
            # If username already exists, use email prefix with employee_id
            if User.objects.filter(username=username).exists():
                username = f"{instance.email.split('@')[0]}_{instance.employee_id}"
            
            # Create new Django User with password (use default if no password set)
            password = instance.password if instance.password else 'changeme123'
            
            user = User.objects.create_user(
                username=username,
                email=instance.email,
                first_name=instance.first_name,
                last_name=instance.last_name,
                password=password,
                is_staff=(instance.role == 'ADMIN'),
                is_superuser=(instance.role == 'ADMIN')
            )
            
            # Add user to "Staff" group
            staff_group, _ = Group.objects.get_or_create(name='Staff')
            user.groups.add(staff_group)
            print(f"Added {user.username} to Staff group")
        else:
            # Update existing user
            try:
                user = User.objects.get(email=instance.email)
                user.first_name = instance.first_name
                user.last_name = instance.last_name
                user.is_staff = (instance.role == 'ADMIN')
                user.is_superuser = (instance.role == 'ADMIN')
                if instance.password and not user.check_password(instance.password):
                    user.set_password(instance.password)
                user.save()
                
                # Ensure user is in "Staff" group
                staff_group, _ = Group.objects.get_or_create(name='Staff')
                if staff_group not in user.groups.all():
                    user.groups.add(staff_group)
                    print(f"Added {user.username} to Staff group on update")
            except User.DoesNotExist:
                # User doesn't exist, create one
                username = instance.employee_id
                if User.objects.filter(username=username).exists():
                    username = f"{instance.email.split('@')[0]}_{instance.employee_id}"
                
                password = instance.password if instance.password else 'changeme123'
                
                user = User.objects.create_user(
                    username=username,
                    email=instance.email,
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    password=password,
                    is_staff=(instance.role == 'ADMIN'),
                    is_superuser=(instance.role == 'ADMIN')
                )
                
                staff_group, _ = Group.objects.get_or_create(name='Staff')
                user.groups.add(staff_group)
                print(f"Created user {user.username} and added to Staff group")
    finally:
        delattr(instance, '_signal_processing')

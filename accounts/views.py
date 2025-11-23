from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from inventory.models import BorrowRecord

def login_view(request):
    """Custom login view that handles admin and user redirection"""
    form = AuthenticationForm()
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect superuser/admin to staff dashboard FIRST
            if user.is_superuser:
                return redirect('staff_dashboard')
            elif user.groups.filter(name='Staff').exists():
                return redirect('staff_dashboard')
            else:
                return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    """User profile and dashboard view"""
    user = request.user
    borrowings = BorrowRecord.objects.filter(user=user).order_by('-borrow_date')
    active_borrowings = borrowings.filter(is_returned=False)
    returned_borrowings = borrowings.filter(is_returned=True)
    
    context = {
        'user': user,
        'borrowings': borrowings,
        'active_borrowings': active_borrowings,
        'returned_borrowings': returned_borrowings,
        'total_borrowed': borrowings.count(),
        'active_count': active_borrowings.count(),
        'returned_count': returned_borrowings.count(),
    }
    return render(request, 'accounts/profile.html', context)

def logout_view(request):
    """Logout view that redirects to login page"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def profile(request):
    """User profile view"""
    user = request.user
    
    # Pending requests - PENDING status
    pending_requests = BorrowRecord.objects.filter(
        user=user,
        status='PENDING'
    ).select_related('asset').order_by('-borrow_date')
    
    # Active borrowings - APPROVED and NOT returned
    active_borrowings = BorrowRecord.objects.filter(
        user=user,
        status='APPROVED',
        is_returned=False
    ).select_related('asset').order_by('-borrow_date')
    
    # Returned borrowings - APPROVED and returned
    returned_borrowings = BorrowRecord.objects.filter(
        user=user,
        status='APPROVED',
        is_returned=True
    ).select_related('asset').order_by('-return_date')
    
    # Statistics
    total_borrowed = BorrowRecord.objects.filter(user=user, status='APPROVED').count()
    active_count = active_borrowings.count()
    returned_count = returned_borrowings.count()
    
    context = {
        'user': user,
        'pending_requests': pending_requests,  # KEY: Match template variable name
        'active_borrowings': active_borrowings,
        'returned_borrowings': returned_borrowings,
        'total_borrowed': total_borrowed,
        'active_count': active_count,
        'returned_count': returned_count,
    }
    return render(request, 'accounts/profile.html', context)
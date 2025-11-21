from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from inventory.models import BorrowRecord

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

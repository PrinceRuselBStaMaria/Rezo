from django.shortcuts import render, redirect, get_object_or_404
from .models import Asset, BorrowRecord
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q

# 1. READ: List all available assets
def asset_list(request):
    # Get all assets (don't filter by status yet)
    assets = Asset.objects.all()
    
    # Filter assets that have available stock
    available_assets = [asset for asset in assets if asset.is_stock_available()]
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        available_assets = [asset for asset in available_assets if search_query.lower() in asset.name.lower() or search_query.lower() in asset.serial_number.lower() or search_query.lower() in asset.category.name.lower()]
    
    context = {
        'assets': available_assets,
    }
    return render(request, 'inventory/asset_list.html', context)

# 2. CREATE/UPDATE: Borrow an item with quantity (Request)
@login_required
def borrow_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate quantity
        if quantity < 1:
            messages.error(request, 'Quantity must be at least 1.')
            return render(request, 'inventory/confirm_borrow.html', {'asset': asset})
        
        # Check available stock
        available_qty = asset.get_available_quantity()
        if quantity > available_qty:
            messages.error(request, f'Not enough stock. Only {available_qty} item(s) available.')
            return render(request, 'inventory/confirm_borrow.html', {'asset': asset})
        
        # Create borrow REQUEST (PENDING status) - NOT automatically approved
        BorrowRecord.objects.create(
            user=request.user,
            asset=asset,
            quantity=quantity,
            status='PENDING',  # This is the key - must be PENDING
            is_returned=False
        )
        
        messages.success(request, f'Your request to borrow {quantity} x {asset.name} has been submitted. Please wait for staff approval.')
        return redirect('my_borrowings')  # Redirect to my_borrowings so user can see their pending request

    return render(request, 'inventory/confirm_borrow.html', {'asset': asset})

# 3. READ: List user's borrowings
@login_required
def my_borrowings(request):
    # Get ALL borrow records for this user
    all_borrowings = BorrowRecord.objects.filter(user=request.user).order_by('-borrow_date')
    
    # Separate by status
    pending_borrowings = all_borrowings.filter(status='PENDING')
    approved_borrowings = all_borrowings.filter(status='APPROVED', is_returned=False)
    rejected_borrowings = all_borrowings.filter(status='REJECTED')
    returned_borrowings = all_borrowings.filter(status='APPROVED', is_returned=True)
    
    context = {
        'borrowings': all_borrowings,  # All records
        'pending_borrowings': pending_borrowings,
        'approved_borrowings': approved_borrowings,
        'rejected_borrowings': rejected_borrowings,
        'returned_borrowings': returned_borrowings,
    }
    return render(request, 'inventory/my_borrowing.html', context)

# 4. UPDATE: Return an item
@login_required
def return_asset(request, pk):
    borrow_record = get_object_or_404(BorrowRecord, pk=pk, user=request.user, status='APPROVED')
    
    if request.method == 'POST':
        borrow_record.is_returned = True
        borrow_record.return_date = timezone.now().date()
        borrow_record.save()
        
        # Update asset status if stock becomes available
        if borrow_record.asset.get_available_quantity() > 0:
            borrow_record.asset.status = 'AVAILABLE'
            borrow_record.asset.save()
        
        messages.success(request, f'You have successfully returned {borrow_record.quantity} x {borrow_record.asset.name}')
        return redirect('my_borrowings')
    
    return render(request, 'inventory/confirm_return.html', {'borrow_record': borrow_record})

def home(request):
    """Homepage view"""
    return render(request, 'index.html')

@login_required
def profile(request):
    """User profile page."""
    # Get all borrowings for the user
    borrowings = BorrowRecord.objects.filter(user=request.user).select_related('asset', 'asset__category').order_by('-borrow_date')

    # Active borrowings (approved but not returned)
    active_borrowings = borrowings.filter(status='APPROVED', is_returned=False)

    # Returned borrowings (approved and returned)
    returned_borrowings = borrowings.filter(status='APPROVED', is_returned=True)

    # Pending requests
    pending_requests = borrowings.filter(status='PENDING')

    # Statistics
    total_borrowed = borrowings.filter(status='APPROVED').count()
    active_count = active_borrowings.count()
    returned_count = returned_borrowings.count()

    context = {
        'total_borrowed': total_borrowed,
        'active_count': active_count,
        'returned_count': returned_count,
        'active_borrowings': active_borrowings,
        'returned_borrowings': returned_borrowings,
        'pending_requests': pending_requests,
    }
    return render(request, 'accounts/profile.html', context)

# ============================================
# STAFF DASHBOARD VIEWS
# ============================================

@login_required
def staff_dashboard(request):
    """Staff dashboard - only accessible to staff/admin"""
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    # Statistics
    total_assets = Asset.objects.count()
    total_borrowed = BorrowRecord.objects.filter(is_returned=False, status='APPROVED').count()
    total_returned = BorrowRecord.objects.filter(is_returned=True).count()
    pending_requests = BorrowRecord.objects.filter(status='PENDING').count()
    available_assets = sum(1 for asset in Asset.objects.all() if asset.is_stock_available())
    
    # Recent borrowings (approved only)
    recent_borrowings = BorrowRecord.objects.filter(status='APPROVED').select_related('user', 'asset').order_by('-borrow_date')[:10]
    
    # Assets by category
    from .models import Category
    categories = Category.objects.all()
    
    context = {
        'total_assets': total_assets,
        'total_borrowed': total_borrowed,
        'total_returned': total_returned,
        'pending_requests': pending_requests,
        'available_assets': available_assets,
        'recent_borrowings': recent_borrowings,
        'categories': categories,
    }
    return render(request, 'inventory/staff/dashboard.html', context)

@login_required
def staff_manage_assets(request):
    """Manage all assets - only for staff"""
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    assets = Asset.objects.all()
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    context = {
        'assets': assets,
        'search_query': search_query,
    }
    return render(request, 'inventory/staff/asset_management.html', context)  # Use the existing filename

@login_required
def staff_reports(request):
    """View reports - only for staff"""
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    return render(request, 'inventory/staff/reports.html')

@login_required
def staff_manage_requests(request):
    """Manage borrow requests - only for staff"""
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    # Get pending requests
    pending_requests = BorrowRecord.objects.filter(status='PENDING').select_related('user', 'asset').order_by('-borrow_date')
    
    context = {
        'pending_requests': pending_requests,
    }
    return render(request, 'inventory/staff/manage_requests.html', context)

@login_required
def staff_approve_request(request, pk):
    """Approve a borrow request"""
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    borrow_record = get_object_or_404(BorrowRecord, pk=pk, status='PENDING')
    
    # Check if stock is still available
    available_qty = borrow_record.asset.get_available_quantity() + borrow_record.quantity  # Add back the pending quantity
    if borrow_record.quantity > available_qty:
        messages.error(request, 'Not enough stock available to approve this request.')
        return redirect('staff_manage_requests')
    
    # APPROVE the request
    borrow_record.status = 'APPROVED'
    borrow_record.approved_by = request.user
    borrow_record.approved_date = timezone.now().date()
    borrow_record.save()
    
    # Update asset status if all stock is borrowed
    if borrow_record.asset.get_available_quantity() <= 0:
        borrow_record.asset.status = 'BORROWED'
        borrow_record.asset.save()
    
    messages.success(request, f'Approved borrow request for {borrow_record.user.username} - {borrow_record.quantity} x {borrow_record.asset.name}')
    return redirect('staff_manage_requests')

@login_required
def staff_reject_request(request, pk):
    """Reject a borrow request"""
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    borrow_record = get_object_or_404(BorrowRecord, pk=pk, status='PENDING')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        borrow_record.status = 'REJECTED'
        borrow_record.rejection_reason = reason
        borrow_record.approved_by = request.user  # Track who rejected it
        borrow_record.save()
        
        messages.success(request, f'Rejected borrow request for {borrow_record.user.username}')
        return redirect('staff_manage_requests')
    
    return render(request, 'inventory/staff/reject_request.html', {'borrow_record': borrow_record})
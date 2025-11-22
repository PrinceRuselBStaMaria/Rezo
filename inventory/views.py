from django.shortcuts import render, redirect, get_object_or_404
from .models import Asset, BorrowRecord
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q

# 1. READ: List all available assets
def asset_list(request):
    assets = Asset.objects.filter(status='AVAILABLE')
    
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

# 2. CREATE/UPDATE: Borrow an item with quantity
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
        
        # Create or update borrow record
        borrow_record, created = BorrowRecord.objects.get_or_create(
            user=request.user,
            asset=asset,
            is_returned=False,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # If record already exists, check if adding more exceeds limit
            new_quantity = borrow_record.quantity + quantity
            if new_quantity > available_qty + borrow_record.quantity:
                messages.error(request, f'Not enough stock. Only {available_qty} item(s) available.')
                return render(request, 'inventory/confirm_borrow.html', {'asset': asset})
            borrow_record.quantity = new_quantity
            borrow_record.save()
        
        # Update asset status if all stock is borrowed
        if asset.get_available_quantity() <= 0:
            asset.status = 'BORROWED'
            asset.save()
        
        messages.success(request, f'You have successfully borrowed {quantity} x {asset.name}')
        return redirect('asset_list')

    return render(request, 'inventory/confirm_borrow.html', {'asset': asset})

# 3. READ: List user's borrowings
@login_required
def my_borrowings(request):
    borrowings = BorrowRecord.objects.filter(user=request.user, is_returned=False)
    return render(request, 'inventory/my_borrowings.html', {'borrowings': borrowings})

# 4. UPDATE: Return an item
@login_required
def return_asset(request, pk):
    borrow_record = get_object_or_404(BorrowRecord, pk=pk, user=request.user)
    
    if request.method == 'POST':
        borrow_record.is_returned = True
        borrow_record.return_date = timezone.now().date()
        borrow_record.save()
        
        # Update asset status if stock becomes available
        if borrow_record.asset.get_available_quantity() > 0:
            borrow_record.asset.status = 'AVAILABLE'
            borrow_record.asset.save()
        
        messages.success(request, f'You have successfully returned {borrow_record.quantity} x {borrow_record.asset.name}')
        return redirect('profile')
    
    return render(request, 'inventory/confirm_return.html', {'borrow_record': borrow_record})

def home(request):
    """Homepage view"""
    return render(request, 'index.html')

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
    total_borrowed = BorrowRecord.objects.filter(is_returned=False).count()
    total_returned = BorrowRecord.objects.filter(is_returned=True).count()
    available_assets = Asset.objects.filter(status='AVAILABLE').count()
    
    # Recent borrowings
    recent_borrowings = BorrowRecord.objects.select_related('user', 'asset').order_by('-borrow_date')[:10]
    
    # Assets by category
    from .models import Category
    categories = Category.objects.all()
    
    context = {
        'total_assets': total_assets,
        'total_borrowed': total_borrowed,
        'total_returned': total_returned,
        'available_assets': available_assets,
        'recent_borrowings': recent_borrowings,
        'categories': categories,
    }
    return render(request, 'inventory/staff/dashboard.html', context)

@login_required
def staff_manage_assets(request):
    """Manage assets - only for staff"""
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    # Get all assets
    assets = Asset.objects.select_related('category').all()
    
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
    return render(request, 'inventory/staff/asset_management.html', context)

@login_required
def staff_reports(request):
    """View reports - only for staff"""
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    # Borrowing statistics
    total_borrows = BorrowRecord.objects.count()
    active_borrows = BorrowRecord.objects.filter(is_returned=False).count()
    returned_borrows = BorrowRecord.objects.filter(is_returned=True).count()
    
    # Most borrowed assets
    most_borrowed = Asset.objects.annotate(
        borrow_count=Sum('borrowrecord__quantity')
    ).order_by('-borrow_count')[:10]
    
    # Recent activity
    recent_activity = BorrowRecord.objects.select_related('user', 'asset').order_by('-borrow_date')[:20]
    
    context = {
        'total_borrows': total_borrows,
        'active_borrows': active_borrows,
        'returned_borrows': returned_borrows,
        'most_borrowed': most_borrowed,
        'recent_activity': recent_activity,
    }
    return render(request, 'inventory/staff/reports.html', context)
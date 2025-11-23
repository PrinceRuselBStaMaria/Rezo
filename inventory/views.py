from django.shortcuts import render, redirect, get_object_or_404
from .models import Asset, BorrowRecord, DisposalRecord, MaintenanceRecord
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import timedelta
from django.http import HttpResponseForbidden 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import uuid

# 1. READ: List all available assets
def asset_list(request):
    """Display available assets with pagination"""
    assets = Asset.objects.filter(status='AVAILABLE').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) | 
            Q(serial_number__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Pagination - 6 assets per page
    paginator = Paginator(assets, 6)
    page = request.GET.get('page', 1)
    
    try:
        assets_page = paginator.page(page)
    except PageNotAnInteger:
        assets_page = paginator.page(1)
    except EmptyPage:
        assets_page = paginator.page(paginator.num_pages)
    
    context = {
        'assets': assets_page,
        'search_query': search_query,
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

@login_required
def staff_manage_returns(request):
    """Manage item returns - only for staff"""
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    # Items currently borrowed (approved, not returned)
    pending_returns = BorrowRecord.objects.filter(
        status='APPROVED',
        is_returned=False
    ).select_related('user', 'asset').order_by('borrow_date')
    
    # Add days_borrowed to each record
    today = timezone.now().date()
    for record in pending_returns:
        record.days_borrowed = (today - record.borrow_date).days
    
    # Recently returned items (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_returns = BorrowRecord.objects.filter(
        status='APPROVED',
        is_returned=True,
        return_date__gte=thirty_days_ago
    ).select_related('user', 'asset').order_by('-return_date')
    
    # Add duration to each record
    for record in recent_returns:
        if record.return_date and record.borrow_date:
            record.duration = (record.return_date - record.borrow_date).days
    
    context = {
        'pending_returns': pending_returns,
        'recent_returns': recent_returns,
    }
    return render(request, 'inventory/staff/manage_returns.html', context)

@login_required
def staff_process_return(request, pk):
    """Process a return request"""
    if not (request.user.is_staff or request.user.groups.filter(name='Staff').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    borrow_record = get_object_or_404(BorrowRecord, pk=pk, status='APPROVED', is_returned=False)
    
    if request.method == 'POST':
        condition = request.POST.get('condition', 'good')
        notes = request.POST.get('notes', '')
        
        # Mark as returned
        borrow_record.is_returned = True
        borrow_record.return_date = timezone.now().date()
        borrow_record.save()
        
        # Update asset status if all stock is available again
        if borrow_record.asset.get_available_quantity() >= borrow_record.asset.total_quantity:
            borrow_record.asset.status = 'AVAILABLE'
            borrow_record.asset.save()
        
        messages.success(request, f'Successfully processed return of {borrow_record.quantity}x {borrow_record.asset.name} from {borrow_record.user.username}')
        return redirect('staff_manage_returns')
    
    return render(request, 'inventory/staff/process_return.html', {'borrow_record': borrow_record})

@login_required
def staff_dispose_asset(request, asset_id):
    """Staff/Admin can directly dispose assets"""
    asset = Asset.objects.get(id=asset_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        reason = request.POST.get('reason')
        
        if quantity > asset.get_available_quantity():
            messages.error(request, 'Quantity exceeds available stock')
            return redirect('staff_manage_assets')
        
        disposal = DisposalRecord.objects.create(
            asset=asset,
            quantity=quantity,
            reason=reason,
            disposed_by=request.user
        )
        
        # Update asset immediately
        asset.total_quantity -= quantity
        asset.save()
        
        messages.success(request, f'Disposed {quantity} units of {asset.name}')
        return redirect('staff_manage_assets')
    
    return render(request, 'inventory/staff/dispose_asset.html', {'asset': asset})

def is_staff_or_admin(user):
    """Check if user is staff or admin"""
    return user.groups.filter(name='Staff').exists() or user.is_superuser

@login_required
def staff_disposal_list(request):
    """View all disposal records"""
    if not is_staff_or_admin(request.user):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    disposals = DisposalRecord.objects.all().select_related('asset', 'disposed_by').order_by('-disposal_date')
    
    context = {
        'disposals': disposals,
    }
    return render(request, 'inventory/staff/disposal_list.html', context)

@login_required
def staff_maintenance_list(request):
    """View all maintenance records"""
    if not is_staff_or_admin(request.user):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    maintenance_records = MaintenanceRecord.objects.all().select_related('asset', 'requested_by', 'assigned_to')
    
    # Separate by status
    pending = maintenance_records.filter(status='PENDING')
    in_progress = maintenance_records.filter(status='IN_PROGRESS')
    completed = maintenance_records.filter(status='COMPLETED')
    
    context = {
        'maintenance_records': maintenance_records,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'pending_count': pending.count(),
        'in_progress_count': in_progress.count(),
    }
    return render(request, 'inventory/staff/maintenance_list.html', context)

@login_required
def staff_create_maintenance(request, asset_id):
    """Create a maintenance request"""
    if not is_staff_or_admin(request.user):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    asset = get_object_or_404(Asset, id=asset_id)
    
    if request.method == 'POST':
        maintenance_type = request.POST.get('maintenance_type')
        description = request.POST.get('description')
        
        MaintenanceRecord.objects.create(
            asset=asset,
            maintenance_type=maintenance_type,
            description=description,
            requested_by=request.user,
            status='PENDING'
        )
        
        # Update asset status to REPAIR
        asset.status = 'REPAIR'
        asset.save()
        
        messages.success(request, f'Maintenance request created for {asset.name}')
        return redirect('staff_maintenance_list')
    
    return render(request, 'inventory/staff/create_maintenance.html', {'asset': asset})

@login_required
def staff_update_maintenance(request, maintenance_id):
    """Update maintenance status (start, complete, cancel)"""
    if not is_staff_or_admin(request.user):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('asset_list')
    
    maintenance = get_object_or_404(MaintenanceRecord, id=maintenance_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start':
            maintenance.status = 'IN_PROGRESS'
            maintenance.start_date = timezone.now().date()
            maintenance.assigned_to = request.user
            messages.success(request, 'Maintenance started.')
            
        elif action == 'complete':
            cost = request.POST.get('cost')
            notes = request.POST.get('notes')
            
            maintenance.status = 'COMPLETED'
            maintenance.completion_date = timezone.now().date()
            maintenance.cost = cost if cost else None
            maintenance.notes = notes
            
            # Update asset status back to AVAILABLE
            maintenance.asset.status = 'AVAILABLE'
            maintenance.asset.save()
            
            messages.success(request, 'Maintenance completed.')
            
        elif action == 'cancel':
            reason = request.POST.get('reason')
            maintenance.status = 'CANCELLED'
            maintenance.notes = f"Cancelled: {reason}"
            
            # Update asset status back to AVAILABLE
            maintenance.asset.status = 'AVAILABLE'
            maintenance.asset.save()
            
            messages.warning(request, 'Maintenance cancelled.')
        
        maintenance.save()
        return redirect('staff_maintenance_list')
    
    return render(request, 'inventory/staff/update_maintenance.html', {'maintenance': maintenance})
from django.shortcuts import render, redirect, get_object_or_404
from .models import Asset, BorrowRecord
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

# 1. READ: List all available assets
def asset_list(request):
    assets = Asset.objects.filter(status='AVAILABLE')
    
    # If user is authenticated, get items they already borrowed
    borrowed_items_ids = []
    if request.user.is_authenticated:
        borrowed_items_ids = BorrowRecord.objects.filter(
            user=request.user, 
            is_returned=False
        ).values_list('asset_id', flat=True)
    
    context = {
        'assets': assets,
        'borrowed_items_ids': list(borrowed_items_ids),
    }
    return render(request, 'inventory/asset_list.html', context)

# 2. CREATE/UPDATE: Borrow an item
@login_required
def borrow_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    
    # Check if user already has this item borrowed
    existing_borrow = BorrowRecord.objects.filter(
        user=request.user,
        asset=asset,
        is_returned=False
    ).exists()
    
    if existing_borrow:
        messages.error(request, f'You already have {asset.name} borrowed. Please return it first.')
        return redirect('asset_list')
    
    if request.method == 'POST':
        # Create borrow record
        BorrowRecord.objects.create(user=request.user, asset=asset)
        # Update asset status
        asset.status = 'BORROWED'
        asset.save()
        messages.success(request, f'You have successfully borrowed {asset.name}')
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
        
        borrow_record.asset.status = 'AVAILABLE'
        borrow_record.asset.save()
        
        messages.success(request, f'You have successfully returned {borrow_record.asset.name}')
        return redirect('profile')
    
    return render(request, 'inventory/confirm_return.html', {'borrow_record': borrow_record})

def home(request):
    """Homepage view"""
    return render(request, 'index.html')
from django.shortcuts import render, redirect, get_object_or_404
from .models import Asset, BorrowRecord
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

# 1. READ: List all available assets
def asset_list(request):
    assets = Asset.objects.filter(status='AVAILABLE')
    
    # Filter assets that have available stock
    available_assets = [asset for asset in assets if asset.is_stock_available()]
    
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
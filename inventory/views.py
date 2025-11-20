from django.shortcuts import render, redirect, get_object_or_404
from .models import Asset, BorrowRecord
from django.contrib.auth.decorators import login_required

# 1. READ: List all available assets
def asset_list(request):
    assets = Asset.objects.filter(status='AVAILABLE')
    return render(request, 'inventory/asset_list.html', {'assets': assets}) # [cite: 164]

# 2. CREATE/UPDATE: Borrow an item
@login_required
def borrow_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk) # [cite: 198]
    
    if request.method == 'POST': # [cite: 199]
        # Create borrow record
        BorrowRecord.objects.create(user=request.user, asset=asset)
        # Update asset status
        asset.status = 'BORROWED'
        asset.save() # [cite: 56]
        return redirect('asset_list')

    return render(request, 'inventory/confirm_borrow.html', {'asset': asset})
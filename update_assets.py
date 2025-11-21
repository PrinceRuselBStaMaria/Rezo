import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rezo.settings')
django.setup()

from inventory.models import Asset, Category

# Get or create gadget category
gadget_category, _ = Category.objects.get_or_create(name='gadget')

# Update the "testing" asset to "tv"
try:
    testing_asset = Asset.objects.get(name='testing')
    testing_asset.name = 'tv'
    testing_asset.serial_number = 'TV001'
    testing_asset.save()
    print(f"✓ Updated 'testing' to 'tv' with serial TV001")
except Asset.DoesNotExist:
    print("✗ 'testing' asset not found")

# Create new assets
new_assets = [
    {'name': 'chair', 'serial_number': 'CHAIR001'},
    {'name': 'chalk', 'serial_number': 'CHALK001'},
    {'name': 'electricfan', 'serial_number': 'FAN001'},
]

for asset_data in new_assets:
    asset, created = Asset.objects.get_or_create(
        serial_number=asset_data['serial_number'],
        defaults={
            'name': asset_data['name'],
            'category': gadget_category,
            'status': 'AVAILABLE'
        }
    )
    if created:
        print(f"✓ Created new asset: {asset_data['name']} (Serial: {asset_data['serial_number']})")
    else:
        print(f"ℹ Asset already exists: {asset_data['name']}")

print("\n✓ All assets have been updated successfully!")

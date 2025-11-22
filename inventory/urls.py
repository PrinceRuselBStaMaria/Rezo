from django.urls import path
from . import views

urlpatterns = [
    path('assets/', views.asset_list, name='asset_list'),
    path('borrow/<int:pk>/', views.borrow_asset, name='borrow_asset'),
    path('my-borrowings/', views.my_borrowings, name='my_borrowings'),
    path('return/<int:pk>/', views.return_asset, name='return_asset'),
    
    # Staff URLs
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/manage-assets/', views.staff_manage_assets, name='staff_manage_assets'),
    path('staff/reports/', views.staff_reports, name='staff_reports'),
]
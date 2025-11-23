from django.urls import path
from . import views

urlpatterns = [
    path('assets/', views.asset_list, name='asset_list'),
    path('borrow/<int:pk>/', views.borrow_asset, name='borrow_asset'),
    path('return/<int:pk>/', views.return_asset, name='return_asset'),
    path('my-borrowings/', views.my_borrowings, name='my_borrowings'),
    
    # Staff URLs
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/manage-assets/', views.staff_manage_assets, name='staff_manage_assets'),
    path('staff/reports/', views.staff_reports, name='staff_reports'),
    path('staff/manage-requests/', views.staff_manage_requests, name='staff_manage_requests'),
    path('staff/approve/<int:pk>/', views.staff_approve_request, name='staff_approve_request'),
    path('staff/reject/<int:pk>/', views.staff_reject_request, name='staff_reject_request'),
    path('staff/manage-returns/', views.staff_manage_returns, name='staff_manage_returns'),
    path('staff/process-return/<int:pk>/', views.staff_process_return, name='staff_process_return'),
    path('staff/disposal/<int:asset_id>/', views.staff_dispose_asset, name='staff_dispose_asset'),
    path('staff/disposal/list/', views.staff_disposal_list, name='staff_disposal_list'),
    # Maintenance URLs
    path('staff/maintenance/', views.staff_maintenance_list, name='staff_maintenance_list'),
    path('staff/maintenance/create/<int:asset_id>/', views.staff_create_maintenance, name='staff_create_maintenance'),
    path('staff/maintenance/update/<int:maintenance_id>/', views.staff_update_maintenance, name='staff_update_maintenance'),
    
    # Damage URLs
    path('staff/mark-repaired/<int:damage_id>/', views.staff_mark_repaired, name='staff_mark_repaired'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('assets/', views.asset_list, name='asset_list'),
    path('borrow/<int:pk>/', views.borrow_asset, name='borrow_asset'),
    path('my-borrowings/', views.my_borrowings, name='my_borrowings'),
    path('return/<int:pk>/', views.return_asset, name='return_asset'),
]
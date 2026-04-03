from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Barcode
    path('barcode/lookup/', views.barcode_lookup, name='barcode_lookup'),
    path('pos/', views.pos_sale, name='pos_sale'),
    path('products/<int:pk>/barcode/', views.product_barcode, name='product_barcode'),

    # Receipts
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipts/<int:pk>/', views.receipt_detail, name='receipt_detail'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),

    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/edit/<int:pk>/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/delete/<int:pk>/', views.supplier_delete, name='supplier_delete'),

    # Sales
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/add/', views.sale_add, name='sale_add'),
    path('mpesa/pay/', views.send_stk_push, name='stk_push'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('mpesa/status/', views.mpesa_payment_status, name='mpesa_status'),
]
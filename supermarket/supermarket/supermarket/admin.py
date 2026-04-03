from django.contrib import admin
from .models import Product, Category, Supplier, Sale


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email']
    search_fields = ['name', 'contact_person']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock_quantity', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'sku']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_sold', 'unit_price', 'total_amount', 'sale_date', 'cashier']
    list_filter = ['sale_date']
    search_fields = ['product__name', 'cashier']

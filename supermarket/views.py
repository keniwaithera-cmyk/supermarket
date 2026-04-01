from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from .models import Product, Category, Supplier, Sale, Receipt, ReceiptItem
from .forms import ProductForm, CategoryForm, SupplierForm, SaleForm
import json
import random


def dashboard(request):
    if request.method == 'POST':
        try:
            cart        = json.loads(request.POST.get('cart_data', '[]'))
            cashier     = request.POST.get('cashier', 'lilian,john')
            amount_paid = float(request.POST.get('amount_paid', 0) or 0)
            tax_rate    = float(request.POST.get('tax_rate', 16) or 16)
            if not cart:
                messages.error(request, 'Cart is empty.')
                return redirect('dashboard')
            errors = []
            for item in cart:
                product = Product.objects.get(pk=item['product_id'])
                if int(item['quantity']) > product.stock_quantity:
                    errors.append(f"Not enough stock for {product.name}.")
            if errors:
                for e in errors: messages.error(request, e)
                return redirect('dashboard')
            subtotal    = sum(float(i['price']) * int(i['quantity']) for i in cart)
            tax_amount  = round(subtotal * (tax_rate / 100), 2)
            grand_total = round(subtotal + tax_amount, 2)
            change      = round(amount_paid - grand_total, 2) if amount_paid >= grand_total else 0
            now = timezone.now()
            receipt = Receipt.objects.create(
                receipt_number=f"RCP-{now.strftime('%Y%m%d')}-{random.randint(1000,9999)}",
                cashier=cashier, total_amount=subtotal,
                tax_rate=tax_rate, tax_amount=tax_amount,
                grand_total=grand_total, amount_paid=amount_paid, change_given=change,
            )
            for item in cart:
                product = Product.objects.get(pk=item['product_id'])
                qty = int(item['quantity']); price = float(item['price'])
                ReceiptItem.objects.create(
                    receipt=receipt, product=product, product_name=product.name,
                    quantity=qty, unit_price=price, subtotal=round(qty * price, 2),
                )
                Sale.objects.create(product=product, quantity_sold=qty, unit_price=price, cashier=cashier)
            return redirect('receipt_detail', pk=receipt.pk)
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('dashboard')

    total_products     = Product.objects.filter(is_active=True).count()
    total_categories   = Category.objects.count()
    total_suppliers    = Supplier.objects.count()
    low_stock          = Product.objects.filter(is_active=True, stock_quantity__lte=10).count()
    recent_sales       = Sale.objects.select_related('product').order_by('-sale_date')[:8]
    total_sales_value  = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    inventory_value    = sum(p.total_value for p in Product.objects.filter(is_active=True))
    low_stock_products = Product.objects.filter(is_active=True, stock_quantity__lte=10).order_by('stock_quantity')[:5]
    recent_receipts    = Receipt.objects.order_by('-created_at')[:5]
    all_products       = Product.objects.filter(is_active=True).order_by('name')
    context = {
        'total_products': total_products, 'total_categories': total_categories,
        'total_suppliers': total_suppliers, 'low_stock': low_stock,
        'recent_sales': recent_sales, 'total_sales_value': total_sales_value,
        'inventory_value': inventory_value, 'low_stock_products': low_stock_products,
        'recent_receipts': recent_receipts, 'all_products': all_products,
    }
    return render(request, 'supermarket/dashboard.html', context)


@require_GET
def barcode_lookup(request):
    code = request.GET.get('code', '').strip()
    if not code:
        return JsonResponse({'found': False, 'error': 'No barcode provided'})
    product = Product.objects.filter(Q(barcode_number=code) | Q(sku=code), is_active=True).first()
    if product:
        return JsonResponse({'found': True, 'id': product.pk, 'name': product.name,
            'sku': product.sku, 'price': str(product.price), 'stock': product.stock_quantity,
            'category': product.category.name if product.category else ''})
    return JsonResponse({'found': False, 'error': f'No product found for: {code}'})


def pos_sale(request):
    if request.method == 'POST':
        try:
            cart        = json.loads(request.POST.get('cart_data', '[]'))
            cashier     = request.POST.get('cashier', '')
            amount_paid = float(request.POST.get('amount_paid', 0) or 0)
            tax_rate    = float(request.POST.get('tax_rate', 0) or 0)
            if not cart:
                messages.error(request, 'Cart is empty.')
                return redirect('pos_sale')
            errors = []
            for item in cart:
                product = Product.objects.get(pk=item['product_id'])
                if int(item['quantity']) > product.stock_quantity:
                    errors.append(f"Not enough stock for {product.name} (only {product.stock_quantity} left).")
            if errors:
                for e in errors: messages.error(request, e)
                return redirect('pos_sale')
            subtotal    = sum(float(i['price']) * int(i['quantity']) for i in cart)
            tax_amount  = round(subtotal * (tax_rate / 100), 2)
            grand_total = round(subtotal + tax_amount, 2)
            change      = round(amount_paid - grand_total, 2) if amount_paid >= grand_total else 0
            now = timezone.now()
            receipt = Receipt.objects.create(
                receipt_number=f"RCP-{now.strftime('%Y%m%d')}-{random.randint(1000,9999)}",
                cashier=cashier, total_amount=subtotal, tax_rate=tax_rate,
                tax_amount=tax_amount, grand_total=grand_total,
                amount_paid=amount_paid, change_given=change,
            )
            for item in cart:
                product = Product.objects.get(pk=item['product_id'])
                qty = int(item['quantity']); price = float(item['price'])
                ReceiptItem.objects.create(
                    receipt=receipt, product=product, product_name=product.name,
                    quantity=qty, unit_price=price, subtotal=round(qty * price, 2),
                )
                Sale.objects.create(product=product, quantity_sold=qty, unit_price=price, cashier=cashier)
            return redirect('receipt_detail', pk=receipt.pk)
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('pos_sale')
    return render(request, 'supermarket/pos_sale.html')


def receipt_detail(request, pk):
    receipt = get_object_or_404(Receipt, pk=pk)
    return render(request, 'supermarket/receipt.html', {'receipt': receipt})


def receipt_list(request):
    receipts = Receipt.objects.all().order_by('-created_at')
    total = receipts.aggregate(total=Sum('grand_total'))['total'] or 0
    return render(request, 'supermarket/receipt_list.html', {'receipts': receipts, 'total': total})


def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    products = Product.objects.select_related('category', 'supplier').filter(is_active=True)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query) | Q(barcode_number__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    categories = Category.objects.all()
    return render(request, 'supermarket/product_list.html', {
        'products': products, 'categories': categories, 'query': query, 'selected_category': category_id})


def product_add(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Product added successfully!')
        return redirect('product_list')
    return render(request, 'supermarket/product_form.html', {'form': form, 'title': 'Add Product', 'show_scanner': True})


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('product_list')
    return render(request, 'supermarket/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product, 'show_scanner': True})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.is_active = False; product.save()
        messages.success(request, 'Product removed!')
        return redirect('product_list')
    return render(request, 'supermarket/confirm_delete.html', {'object': product, 'type': 'Product'})


def product_barcode(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'supermarket/product_barcode.html', {'product': product})


def category_list(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    return render(request, 'supermarket/category_list.html', {'categories': categories})


def category_add(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, 'Category added!')
        return redirect('category_list')
    return render(request, 'supermarket/product_form.html', {'form': form, 'title': 'Add Category'})


def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save(); messages.success(request, 'Category updated!')
        return redirect('category_list')
    return render(request, 'supermarket/product_form.html', {'form': form, 'title': 'Edit Category'})


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete(); messages.success(request, 'Category deleted!')
        return redirect('category_list')
    return render(request, 'supermarket/confirm_delete.html', {'object': category, 'type': 'Category'})


def supplier_list(request):
    suppliers = Supplier.objects.annotate(product_count=Count('products'))
    return render(request, 'supermarket/supplier_list.html', {'suppliers': suppliers})


def supplier_add(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, 'Supplier added!')
        return redirect('supplier_list')
    return render(request, 'supermarket/product_form.html', {'form': form, 'title': 'Add Supplier'})


def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=supplier)
    if form.is_valid():
        form.save(); messages.success(request, 'Supplier updated!')
        return redirect('supplier_list')
    return render(request, 'supermarket/product_form.html', {'form': form, 'title': 'Edit Supplier'})


def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete(); messages.success(request, 'Supplier deleted!')
        return redirect('supplier_list')
    return render(request, 'supermarket/confirm_delete.html', {'object': supplier, 'type': 'Supplier'})


def sale_list(request):
    sales = Sale.objects.select_related('product').order_by('-sale_date')
    total = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    return render(request, 'supermarket/sale_list.html', {'sales': sales, 'total': total})


def sale_add(request):
    form = SaleForm(request.POST or None)
    if form.is_valid():
        sale = form.save(commit=False)
        if sale.quantity_sold > sale.product.stock_quantity:
            messages.error(request, f'Not enough stock! Only {sale.product.stock_quantity} available.')
        else:
            sale.save(); messages.success(request, 'Sale recorded!')
            return redirect('sale_list')
    return render(request, 'supermarket/product_form.html', {'form': form, 'title': 'Record Sale'})
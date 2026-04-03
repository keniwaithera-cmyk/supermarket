from django.db import models
from django.utils import timezone


# ─────────────────────────────────────────
# CATEGORY
# ─────────────────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


# ─────────────────────────────────────────
# SUPPLIER
# ─────────────────────────────────────────
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ─────────────────────────────────────────
# PRODUCT
# ─────────────────────────────────────────
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)  # ← ADD THIS LINE
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    barcode_number = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
# ─────────────────────────────────────────
# SALE
# ─────────────────────────────────────────
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity_sold = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cashier = models.CharField(max_length=100, blank=True, null=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-calculate total_amount
        self.total_amount = self.unit_price * self.quantity_sold
        # Deduct from stock
        if not self.pk:
            self.product.stock_quantity -= self.quantity_sold
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x{self.quantity_sold} on {self.sale_date.strftime('%Y-%m-%d')}"


# ─────────────────────────────────────────
# RECEIPT
# ─────────────────────────────────────────
class Receipt(models.Model):
    receipt_number = models.CharField(max_length=50, unique=True)
    cashier = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    change_given = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.receipt_number


# ─────────────────────────────────────────
# RECEIPT ITEM
# ─────────────────────────────────────────
class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"


# ─────────────────────────────────────────
# MPESA TRANSACTION
# ─────────────────────────────────────────
class MpesaTransaction(models.Model):
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_code = models.CharField(max_length=50)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mpesa_code} - KES {self.amount}"


# ─────────────────────────────────────────
# MPESA PAYMENT (optional — for linking to receipt)
# ─────────────────────────────────────────
class MpesaPayment(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.SET_NULL, null=True, blank=True)
    transaction = models.ForeignKey(MpesaTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MpesaPayment #{self.pk}"
from django.db import models
from io import BytesIO
from django.core.files import File


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    sku = models.CharField(max_length=50, unique=True)
    barcode_number = models.CharField(max_length=100, blank=True, help_text="Scanned or manual barcode (defaults to SKU)")
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    description = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level
    @property
    def total_value(self):
        return self.price * self.stock_quantity
    def generate_barcode(self):
        try:
            import barcode
            from barcode.writer import ImageWriter
            code = self.barcode_number or self.sku
            EAN = barcode.get_barcode_class('code128')
            ean = EAN(code, writer=ImageWriter())
            buffer = BytesIO()
            ean.write(buffer, options={
                'module_width': 0.8, 'module_height': 8.0,
                'font_size': 6, 'text_distance': 2.0,
                'quiet_zone': 2.0, 'write_text': True
            })
            self.barcode_image.save(f'barcode_{self.sku}.png', File(buffer), save=False)
        except Exception as e:
            print(f"Barcode error: {e}")
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_sku = None
        if not is_new:
            try:
                old_sku = Product.objects.get(pk=self.pk).sku
            except Product.DoesNotExist:
                pass
        if not self.barcode_number:
            self.barcode_number = self.sku
        super().save(*args, **kwargs)
        if is_new or old_sku != self.sku:
            self.generate_barcode()
            Product.objects.filter(pk=self.pk).update(barcode_image=self.barcode_image)


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity_sold = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    cashier = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    class Meta:
        ordering = ['-sale_date']
    def __str__(self):
        return f"Sale of {self.product.name} on {self.sale_date.strftime('%Y-%m-%d')}"
    def save(self, *args, **kwargs):
        self.total_amount = self.quantity_sold * self.unit_price
        super().save(*args, **kwargs)
        self.product.stock_quantity -= self.quantity_sold
        self.product.save()


class Receipt(models.Model):
    receipt_number = models.CharField(max_length=20, unique=True)
    cashier = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    change_given = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"Receipt #{self.receipt_number}"


class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
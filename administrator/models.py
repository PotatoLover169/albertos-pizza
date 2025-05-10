from django.db import models
from django.contrib.auth.models import User

# Menu Items Models
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class MenuItemVariant(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)  # e.g., "Small", "Medium", "Large"
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.name}"

class MenuItemAddon(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Extra Cheese", "Mushrooms"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

# Customer Models
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

# Order Models
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Payment'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    is_paid = models.BooleanField(default=False)
    delivery_address = models.TextField()
    special_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_id = last_order.id
            else:
                last_id = 0
            self.order_number = f"ORD-{last_id + 1:04d}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    variant = models.ForeignKey(MenuItemVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class OrderItemAddon(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='addons')
    addon = models.ForeignKey(MenuItemAddon, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.addon.name} for {self.order_item}"

# Reports Models
class DailySales(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.PositiveIntegerField()
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Sales for {self.date}"
    
    class Meta:
        verbose_name_plural = "Daily Sales"

# Settings Models
class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Alberto's Pizza")
    logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    opening_hours = models.TextField(default="Monday - Friday: 11am - 10pm\nSaturday - Sunday: 12pm - 11pm")
    
    def __str__(self):
        return self.site_name
    
    class Meta:
        verbose_name_plural = "Site Settings"

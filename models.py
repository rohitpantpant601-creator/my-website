from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# 1. Choices
SIZE_CHOICES = (
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
    ('XL', 'Extra Large'),
)

PAYMENT_CHOICES = [
    ('ONLINE', 'Online Payment'),
    ('COD', 'Cash on Delivery'),
]

# 2. Seller Model
class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    store_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    joined_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self): 
        return self.store_name

# 3. Product Model
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True) 
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self): 
        return self.name
    
    def get_absolute_url(self): 
        return reverse('product_detail', args=[str(self.id)])

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_gallery/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"

# 4. Cart Models
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return f"Cart - {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='M')

    def total_price(self): 
        return self.product.price * self.quantity

# 5. Order Model (Sirf Ek Baar - Optimized)
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment fields
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='ONLINE')
    paid = models.BooleanField(default=False)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='M')

    def get_total_item_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"Item ID {self.id} in Order {self.order.id}"
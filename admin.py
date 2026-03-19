from django.contrib import admin
from .models import Product, ProductImage, Seller, Cart, Order, OrderItem

# 1. Yahan se Product hata diya gaya hai taaki double registration na ho
admin.site.register(Seller)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)

# 2. ProductImage ko Product ke andar dikhane ke liye Inline class
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

# 3. Sirf yahan Product register hoga (Inline ke saath)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
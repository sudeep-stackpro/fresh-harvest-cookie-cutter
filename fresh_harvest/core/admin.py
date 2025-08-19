from django.contrib import admin
from .models import (
    ProductImage,
    User,
    Product,
    Farmer,
    Farm,
    FarmProduct,
    Cart,
    CartItem,
    Review,
    Discount,
    Order,
    OrderItem,
    Recipe,
)

# Register your models here.
admin.site.register(Product)
admin.site.register(Farmer)
admin.site.register(Farm)
admin.site.register(FarmProduct)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Review)
admin.site.register(Discount)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Recipe)
admin.site.register(ProductImage)

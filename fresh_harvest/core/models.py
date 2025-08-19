from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from decimal import Decimal
from django.utils import timezone
from fresh_harvest.users.models import User


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Farmer(TimeStampedModel):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name


class Farm(TimeStampedModel):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="farms")
    name = models.CharField(max_length=50)
    description = models.TextField()
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class FarmProduct(TimeStampedModel):
    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="farm_products"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="farm_products"
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    label = models.CharField(max_length=50, null=True, blank=True)
    harvest_date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.farm.name} {self.product.name}"


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        FarmProduct, on_delete=models.CASCADE, related_name="images"
    )
    image = models.FileField(null=True, blank=True)


class Cart(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return self.user.name


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(FarmProduct, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.cart.user.name} {self.product.product.name}"


class Review(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    farm_product = models.ForeignKey(
        FarmProduct, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(
        default=5, validators=[MaxValueValidator(5), MinValueValidator(1)]
    )
    description = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.name if self.user else 'Anonymous'} rating: {self.rating}"


class Discount(TimeStampedModel):
    coupon_code = models.CharField(max_length=20, primary_key=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.coupon_code


class Order(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_bill = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30)
    coupon = models.ForeignKey(
        Discount, blank=True, null=True, on_delete=models.SET_NULL
    )
    address = models.TextField()

    def __str__(self):
        return self.user.name


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    farm_product = models.ForeignKey(FarmProduct, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = (("order", "farm_product"),)

    def __str__(self):
        return f"{self.order.user.name} {self.farm_product.product.name}"


class Recipe(TimeStampedModel):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, related_name="recipes")

    def __str__(self):
        return self.name

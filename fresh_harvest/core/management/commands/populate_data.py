import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from fresh_harvest.users.models import User
from fresh_harvest.core.models import (
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

fake = Faker()


class Command(BaseCommand):
    help = "Populate the database with sample data for testing"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Deleting old data..."))
        Product.objects.all().delete()
        Farmer.objects.all().delete()
        Farm.objects.all().delete()
        FarmProduct.objects.all().delete()
        Cart.objects.all().delete()
        Review.objects.all().delete()
        Discount.objects.all().delete()
        Order.objects.all().delete()
        Recipe.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write(self.style.SUCCESS("Creating sample data..."))

        # Create Users
        users = []
        for _ in range(5):
            user = User.objects.create_user(
                name=fake.name(),
                email_or_phone=fake.unique.email(),
                password="password123",
                location=fake.city(),
            )
            users.append(user)

        # Create Farmers
        farmers = []
        for _ in range(3):
            farmer = Farmer.objects.create(name=fake.company(), description=fake.text())
            farmers.append(farmer)

        # Create Farms
        farms = []
        for farmer in farmers:
            for _ in range(2):
                farm = Farm.objects.create(
                    farmer=farmer,
                    name=fake.word().capitalize() + " Farm",
                    description=fake.text(),
                    location=fake.city(),
                )
                farms.append(farm)

        # Create Products
        product_types = ["Vegetable", "Fruit", "Grain", "Dairy"]
        products = []
        for _ in range(10):
            product = Product.objects.create(
                name=fake.word().capitalize(),
                description=fake.text(),
                type=random.choice(product_types),
            )
            products.append(product)

        # Farm Products
        farm_products = []
        for farm in farms:
            for product in random.sample(products, 3):
                fp = FarmProduct.objects.create(
                    farm=farm,
                    product=product,
                    quantity=random.randint(10, 100),
                    price=Decimal(random.randint(50, 500)) / 10,
                    label=fake.word(),
                    harvest_date=timezone.now().date(),
                )
                farm_products.append(fp)

        # Carts + Items
        for user in users:
            cart = Cart.objects.create(user=user)
            for fp in random.sample(farm_products, 2):
                CartItem.objects.create(
                    cart=cart, product=fp, quantity=random.randint(1, 5)
                )

        # Reviews
        for fp in farm_products[:5]:
            for user in random.sample(users, 2):
                Review.objects.create(
                    user=user,
                    farm_product=fp,
                    rating=random.randint(1, 5),
                    description=fake.text(),
                    likes=random.randint(0, 20),
                    dislikes=random.randint(0, 5),
                    date=timezone.now().date(),
                )

        # Discounts
        discounts = []
        for code in ["WELCOME10", "FRESH20", "HARVEST5"]:
            d = Discount.objects.create(
                coupon_code=code, discount_percent=random.choice([5, 10, 20])
            )
            discounts.append(d)

        # Orders + Order Items
        for user in users:
            order = Order.objects.create(
                user=user,
                total_bill=Decimal("0.00"),
                status=random.choice(["Pending", "Shipped", "Delivered"]),
                coupon=random.choice(discounts + [None]),
            )
            total = Decimal("0.00")
            for fp in random.sample(farm_products, 2):
                qty = Decimal(random.randint(1, 5))
                OrderItem.objects.create(order=order, farm_product=fp, quantity=qty)
                total += fp.price * qty
            order.total_bill = total
            order.save()

        # Recipes
        for _ in range(3):
            recipe = Recipe.objects.create(name=fake.word().capitalize() + " Recipe")
            recipe.products.set(random.sample(products, 3))

        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))

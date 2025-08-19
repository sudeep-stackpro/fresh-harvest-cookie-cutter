from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    User,
    Product,
    Farmer,
    Farm,
    FarmProduct,
    ProductImage,
    Cart,
    CartItem,
    Review,
    Discount,
    Order,
    OrderItem,
    Recipe,
)


class CoreUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "email_or_phone", "location", "image", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email_or_phone = data.get("email_or_phone")
        password = data.get("password")
        if not email_or_phone or not password:
            raise serializers.ValidationError(
                "Both email_or_phone and password are required."
            )
        user = authenticate(username=email_or_phone, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data["user"] = user
        return data


class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ["id", "name", "description"]


class FarmerSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ["id", "name", "description"]


class FarmSerializer(serializers.ModelSerializer):
    farmer = FarmerSimpleSerializer(read_only=True)
    farmer_id = serializers.PrimaryKeyRelatedField(
        queryset=Farmer.objects.all(), source="farmer", write_only=True
    )

    class Meta:
        model = Farm
        fields = ["id", "farmer", "farmer_id", "name", "description", "location"]


class FarmSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ["id", "name", "description", "location"]


class ProductSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "type", "description"]


class RecipeSerializer(serializers.ModelSerializer):
    products = ProductSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ["id", "name", "products"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "user_name",
            "rating",
            "description",
            "likes",
            "dislikes",
            "date",
        ]


class FarmProductSerializer(serializers.ModelSerializer):
    farm = FarmSerializer(read_only=True)
    product = ProductSimpleSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = FarmProduct
        fields = [
            "id",
            "farm",
            "product",
            "quantity",
            "price",
            "label",
            "harvest_date",
            "images",
            "reviews",
        ]


class FarmProductSimpleSerializer(serializers.ModelSerializer):
    farm = FarmSimpleSerializer(read_only=True)
    product = ProductSimpleSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = FarmProduct
        fields = ["id", "farm", "product", "price", "label", "images"]


class CartItemAddSerializer(serializers.Serializer):
    farm_product_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_farm_product_id(self, value):
        if not FarmProduct.objects.filter(id=value).exists():
            raise serializers.ValidationError("Farm product does not exist.")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    product = FarmProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=FarmProduct.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "cart_items"]


class OrderItemSerializer(serializers.ModelSerializer):
    farm_product = FarmProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "farm_product", "quantity"]


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ["coupon_code", "discount_percent"]
        read_only_fields = ["coupon_code", "discount_percent"]


class OrderDetailSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "total_bill",
            "ordered_at",
            "status",
            "coupon",
            "address",
            "order_items",
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderCreateSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = ["coupon_code", "address"]

    def create(self, validated_data):
        user = self.context["request"].user
        coupon_code = validated_data.get("coupon_code")
        address = validated_data.get("address")
        coupon = None

        if coupon_code:
            try:
                coupon = Discount.objects.get(coupon_code=coupon_code)
            except Discount.DoesNotExist:
                pass

        cart_items = CartItem.objects.filter(cart__user=user)
        if not cart_items.exists():
            raise serializers.ValidationError("Cart is empty")

        total_bill = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=user,
            total_bill=total_bill,
            status="pending",
            coupon=coupon,
            address=address,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order, farm_product=item.product, quantity=item.quantity
            )

        cart_items.delete()

        return order

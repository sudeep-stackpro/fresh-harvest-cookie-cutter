from rest_framework import viewsets, status, permissions, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import (
    Farmer,
    FarmProduct,
    Cart,
    CartItem,
    Discount,
    Order,
    Review,
    User,
    Recipe,
)
from .serializers import (
    CartSerializer,
    CartItemAddSerializer,
    FarmProductSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    FarmerSerializer,
    DiscountSerializer,
    OrderSerializer,
    RecipeSerializer,
    ReviewSerializer,
    CoreUserSerializer,
)


class UserCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CoreUserSerializer
    permission_classes = [permissions.AllowAny]

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemAddSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart).select_related("product")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def list(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # serializer = CartSerializer(cart)
        serializer = CartSerializer(cart, context={"request": request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        farm_product = get_object_or_404(
            FarmProduct, id=serializer.validated_data["farm_product_id"]
        )
        quantity = serializer.validated_data["quantity"]

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=farm_product,
            defaults={"quantity": quantity},
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(
            {"message": "Item added to cart successfully"},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def increase(self, request, pk=None):
        cart_item = get_object_or_404(self.get_queryset(), pk=pk)
        cart_item.quantity += 1
        cart_item.save()
        return Response(
            {"message": f"Quantity increased to {cart_item.quantity}"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def decrease(self, request, pk=None):
        cart_item = get_object_or_404(self.get_queryset(), pk=pk)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            return Response(
                {"message": f"Quantity decreased to {cart_item.quantity}"},
                status=status.HTTP_200_OK,
            )
        else:
            cart_item.delete()
            return Response(
                {"message": "Item removed from cart"},
                status=status.HTTP_200_OK,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Cart item removed successfully"},
            status=status.HTTP_200_OK,
        )


class FarmProductViewSet(viewsets.ModelViewSet):
    queryset = FarmProduct.objects.select_related("farm", "product").prefetch_related(
        "images", "reviews"
    )
    serializer_class = FarmProductSerializer

    def retrieve(self, request, pk=None):
        try:
            product = FarmProduct.objects.get(pk=pk)
        except product.DoesNotExist:
            return Response(
                {"error": "No Such Product"}, status=status.HTTP_204_NO_CONTENT
            )
        serializer = FarmProductSerializer(product)
        return Response(serializer.data)


class SearchProductsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FarmProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = FarmProduct.objects.all()
        product_name = self.request.query_params.get("name")
        if product_name:
            queryset = queryset.filter(product__name__icontains=product_name)
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return OrderDetailSerializer
        elif self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        order_id = serializer.instance.id
        return Response(
            {"message": "Order created successfully", "order_id": order_id},
            status=status.HTTP_201_CREATED,
        )


class FarmerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Farmer.objects.all().order_by("name")
    serializer_class = FarmerSerializer


class DiscountViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "coupon_code"
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    @action(detail=True, methods=["patch"])
    def increase_like(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewSerializer
        if serializer.is_valid():
            review.likes += 1
            review.save()
            return Response({"status": "like updated"}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def increase_dislike(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewSerializer
        if serializer.is_valid():
            review.dislikes += 1
            review.save()
            return Response(
                {"status": "dislike updated"}, status=status.HTTP_202_ACCEPTED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

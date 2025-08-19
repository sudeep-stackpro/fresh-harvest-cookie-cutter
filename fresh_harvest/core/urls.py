from rest_framework.routers import DefaultRouter
from django.urls import path, include

# from .views import (
#     ProductViewSet,
#     FarmerViewSet,
#     FarmViewSet,
#     FarmProductViewSet,
#     ProductImageViewSet,
#     CartViewSet,
#     CartItemViewSet,
#     ReviewViewSet,
#     DiscountViewSet,
#     OrderViewSet,
#     OrderItemViewSet,
#     RecipeViewSet,
#     SearchProductsViewSet,
#     UserCreateViewSet,
#     UserViewSet,
# )

from .views import (
    CartItemViewSet,
    FarmProductViewSet,
    OrderViewSet,
    FarmerViewSet,
    DiscountViewSet,
    RecipeViewSet,
    UserCreateViewSet,
    SearchProductsViewSet,
)


from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = "core"

router = DefaultRouter()

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

router.register("users", UserCreateViewSet, basename="user")
router.register("cart", CartItemViewSet, basename="cart")
router.register("farm-products", FarmProductViewSet, basename="farmproduct")
router.register("orders", OrderViewSet, basename="order")
router.register("farmers", FarmerViewSet, basename="farmer")
router.register("discounts", DiscountViewSet, basename="discount")
router.register("search", SearchProductsViewSet, basename="search")
router.register("recipe", RecipeViewSet, basename="recipe")

urlpatterns += router.urls

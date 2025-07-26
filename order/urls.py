from django.urls import path
from .views import *

urlpatterns = [
    path('my-cart/', CartView.as_view(), name='my-cart'),
    path('add-to-cart/<int:product_id>/', AddToCartView.as_view(), name='add-to-cart'),
]
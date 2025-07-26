from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import *

class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = request.user.cartitem_set.all()

        context = {
            'cart_items': cart_items,
        }
        return render(request, 'cart.html', context)


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        CartItem.objects.create(
            product=get_object_or_404(Product, id=product_id),
            user=request.user
        )
        return redirect('my-cart')
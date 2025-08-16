from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .models import *

class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = request.user.cartitem_set.all()
        wishlist_products = request.user.favorite_set.values_list('product__id', flat=True)

        # Discounts
        total_discount = 0
        total_price_without_discount = 0
        for cart_item in cart_items:
            total_price_without_discount += cart_item.product.price * cart_item.amount
            if cart_item.product.discount_set.filter(end_date__lt=datetime.today()).exists():
                discount = cart_item.product.discount_set.filter(end_date__lt=datetime.today()).last().amount * cart_item.amount
                total_discount += discount

        total_price = total_price_without_discount - total_discount

        context = {
            'cart_items': cart_items,
            'wishlist_products': wishlist_products,
            'total_discount': total_discount,
            'total_price_without_discount': total_price_without_discount,
            'total_price': total_price,
        }
        return render(request, 'cart.html', context)


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart_items = CartItem.objects.filter(
            product=product, user=request.user
        )
        if cart_items.exists():
            cart_item = cart_items.first()
            cart_item.amount += 1
            cart_item.save()
            return redirect('my-cart')

        CartItem.objects.create(
            product=product,
            user=request.user
        )
        return redirect('my-cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        CartItem.objects.filter(
            product=get_object_or_404(Product, id=product_id),
            user=request.user
        ).delete()
        return redirect('my-cart')


def cart_item_inc(request, cart_item_id):
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.amount += 1
        cart_item.save()
        return redirect('my-cart')
    return redirect('login')


def cart_item_dec(request, cart_item_id):
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        if cart_item.amount == 1:
            cart_item.delete()
            return redirect('my-cart')
        cart_item.amount -= 1
        cart_item.save()
        return redirect('my-cart')
    return redirect('login')


class OrderView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'order.html')

    def post(self, request):
        order = Order.objects.create(
            user=request.user,
            first_name=self.request.POST.get('first_name', request.user.first_name),
            last_name=self.request.POST.get('last_name', request.user.last_name),
            phone_number=self.request.POST.get('phone_number', request.user.phone),
            country=self.request.POST.get('country', request.user.country),
            city=self.request.POST.get('city', request.user.city),
            address=self.request.POST.get('address'),
            delivery_type=self.request.POST.get('delivery_type'),
        )

        # Delivery price
        if order.delivery_type == "Fast":
            order.total_price = 20
        else:
            order.total_price = 0

        cart_items = request.user.cartitem_set.all()

        total_discount = 0
        total_price_without_discount = 0
        for cart_item in cart_items:
            total_price_without_discount += cart_item.product.price * cart_item.amount
            if cart_item.product.discount_set.filter(end_date__lt=datetime.today()).exists():
                discount = cart_item.product.discount_set.filter(
                    end_date__lt=datetime.today()).last().amount * cart_item.amount
                total_discount += discount

        total_price = total_price_without_discount - total_discount
        order.total_price = total_price
        order.save()

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                amount=cart_item.amount,
            )
        cart_items.delete()
        return redirect('my-cart')


class OrdersView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user)

        context = {
            'orders': orders,
        }
        return render(request, 'profile-orders.html', context)
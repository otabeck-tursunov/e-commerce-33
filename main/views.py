from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import *

class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            banner_index = 1
            banners = Banner.objects.all()
            categories = Category.objects.all()
            context = {
                'banners': banners,
                'banner_index': banner_index,
                'categories': categories,
            }
            return render(request, 'index.html', context)
        return render(request, 'index-unauth.html')


class CategoryView(LoginRequiredMixin, View):
    def get(self, request, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        context = {
            'category': category,
        }
        return render(request, 'category.html', context)


class SubCategoryView(LoginRequiredMixin, View):
    def get(self, request, category_slug, subcategory_slug):
        subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
        products = Product.objects.filter(sub_category=subcategory).order_by('rating')

        countries = products.values_list('country', flat=True).distinct()
        brands = products.values_list('brand', flat=True).distinct()

        view = request.GET.get('view')
        filter_countries = request.GET.getlist('country')
        filter_brands = request.GET.getlist('brand')
        min_price = request.GET.get('min_price') if request.GET.get('min_price') != "" else None
        max_price = request.GET.get('max_price') if request.GET.get('max_price') != "" else None

        if filter_countries:
            products = products.filter(country__in=filter_countries)
        if filter_brands:
            products = products.filter(brand__in=filter_brands)
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

        context = {
            'subcategory': subcategory,
            'view': view,
            'products': products,
            'countries': countries,
            'filter_countries': filter_countries,
            'brands': brands,
            'filter_brands': filter_brands,
            'min_price': min_price,
            'max_price': max_price,
        }

        if view is not None:
            if view == 'large':
                return render(request, 'sub-products-large.html', context)
        return render(request, 'sub-products-grid.html', context)


class ProductView(LoginRequiredMixin, View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        # IMAGE CHANGE
        main_image_index = request.GET.get('mainImage')
        if main_image_index is None:
            main_image_index = 0
        main_image_index = int(main_image_index)

        main_image = product.image_set.all()[main_image_index]

        # DISCOUNT CALCULATE
        discounts = product.discount_set.all()
        if discounts.exists():
            discount = discounts.last()
            if discount.end_date < datetime.now():
                discount = None
        else:
            discount = None

        # RATING PERCENTAGE
        rating_percentage = product.rating / 5 * 100

        context = {
            'product': product,
            'mainImage': main_image,
            'discount': discount,
            'rating_percentage': rating_percentage,
        }
        print(rating_percentage)
        print(product.review_set.all().values_list('rating', flat=True))

        return render(request, 'product-info.html', context)

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        Review.objects.create(
            product=product,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment'),
            user=request.user
        )

        ratings = product.review_set.all().values_list('rating', flat=True)

        product.rating = sum(ratings) / len(ratings)
        product.save()

        return self.get(request, slug)


class WishListView(LoginRequiredMixin, View):
    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        context = {
            'favorites': favorites,
        }
        return render(request, 'wishlist.html', context)


class AddToWishListView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        favorites = Favorite.objects.filter(user=request.user, product=product)
        if favorites.exists():
            return redirect('wishlist')

        Favorite.objects.create(
            user=request.user, product=product
        )
        return redirect('wishlist')


class RemoveFromWishListView(LoginRequiredMixin, View):
    def get(self, request, favorite_id):
        favorite = get_object_or_404(Favorite, id=favorite_id)
        favorite.delete()
        return redirect('wishlist')


class AddToWishListForCartView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        favorites = Favorite.objects.filter(user=request.user, product=product)
        if favorites.exists():
            favorites.delete()
            return redirect('my-cart')

        Favorite.objects.create(
            user=request.user, product=product
        )
        return redirect('my-cart')
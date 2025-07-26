from _ast import Sub

from django.contrib import admin
from .models import *

admin.site.register(Banner)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(Image)


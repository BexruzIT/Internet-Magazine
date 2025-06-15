from django.contrib import admin

from backend.apps.products.models import Category, Product, SubCategory

admin.site.register([Category, Product, SubCategory])

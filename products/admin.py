from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['parent']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'stock', 'category', 'featured', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category', 'featured', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'featured']
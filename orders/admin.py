from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'email']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['stripe_payment_id', 'created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']
    raw_id_fields = ['order', 'product']
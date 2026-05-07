from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.decorators.http import require_POST

from products.models import Product
from .models import Cart, CartItem


def _get_or_create_cart(request):
    """Get or create a cart for the current user/session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={'session_key': ''}
        )
        # Merge guest cart if exists
        session_key = request.session.session_key
        if session_key:
            guest_cart = Cart.objects.filter(
                session_key=session_key, user__isnull=True
            ).first()
            if guest_cart:
                for item in guest_cart.items.all():
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart, product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    if not created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                guest_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            user__isnull=True
        )
        return cart


def cart_detail(request):
    cart = _get_or_create_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if product.stock < quantity:
        messages.error(request, f"Not enough stock. Only {product.stock} available.")
        return redirect('products:product_detail', slug=product.slug)

    cart = _get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        if cart_item.quantity > product.stock:
            messages.error(request, f"Not enough stock. Only {product.stock} available.")
            return redirect('products:product_detail', slug=product.slug)
        cart_item.save()

    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart:cart_detail')


@require_POST
def update_cart(request, item_id):
    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
    elif quantity > cart_item.product.stock:
        messages.error(request, f"Not enough stock. Only {cart_item.product.stock} available.")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Cart updated.")

    return redirect('cart:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    cart_item.delete()
    messages.success(request, f"{cart_item.product.name} removed from cart.")
    return redirect('cart:cart_detail')
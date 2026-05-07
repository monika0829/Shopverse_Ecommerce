from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings as django_settings

from cart.models import Cart, CartItem
from .models import Order, OrderItem
from .forms import CheckoutForm

import stripe

stripe.api_key = django_settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                zip_code=form.cleaned_data['zip_code'],
                total=cart.total_price,
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity,
                )
                # Decrement stock
                product = item.product
                product.stock = max(0, product.stock - item.quantity)
                product.save()

            # Attempt Stripe payment (test mode)
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total * 100),  # cents
                    currency='usd',
                    metadata={'order_id': order.pk},
                )
                order.stripe_payment_id = intent.id
                order.save()
            except stripe.error.StripeError:
                # In test/dev, continue without valid Stripe
                pass

            # Clear cart
            cart.items.all().delete()
            cart.delete()

            messages.success(request, "Order placed successfully!")
            return redirect('orders:order_confirmation', pk=order.pk)
    else:
        # Pre-fill form from user data
        initial = {
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial)

    context = {
        'form': form,
        'cart': cart,
        'stripe_public_key': django_settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_confirmation(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
from .models import Cart, CartItem


def cart_context(request):
    """Add cart item count to all templates."""
    item_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        cart = Cart.objects.filter(
            session_key=session_key, user__isnull=True
        ).first() if session_key else None

    if cart:
        item_count = cart.total_items

    return {'cart_item_count': item_count}
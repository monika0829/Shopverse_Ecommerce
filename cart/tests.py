from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Category, Product
from .models import Cart, CartItem


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product", price=29.99, stock=10, category=self.category
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)

    def test_cart_str_authenticated(self):
        self.assertIn('testuser', str(self.cart))

    def test_cart_str_guest(self):
        guest_cart = Cart.objects.create(session_key='abc123xyz')
        self.assertIn('abc123xy', str(guest_cart))

    def test_total_price_empty(self):
        self.assertEqual(self.cart.total_price, 0)

    def test_total_price_with_items(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        from decimal import Decimal
        self.assertEqual(self.cart.total_price, Decimal('59.98'))

    def test_total_items(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(self.cart.total_items, 3)


class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product", price=49.99, stock=10, category=self.category
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_item_creation(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(item.quantity, 2)

    def test_cart_item_subtotal(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(item.subtotal, 149.97)

    def test_cart_item_str(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        self.assertIn("Test Product", str(item))

    def test_cart_item_unique_together(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)


class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product", price=29.99, stock=10, category=self.category
        )

    def test_cart_detail_view(self):
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart(self):
        response = self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        self.assertEqual(response.status_code, 302)
        # Verify cart was created
        cart = Cart.objects.first()
        self.assertIsNotNone(cart)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_add_to_cart_insufficient_stock(self):
        response = self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 20}
        )
        self.assertEqual(response.status_code, 302)
        # Cart should not have been created
        self.assertEqual(Cart.objects.count(), 0)

    def test_update_cart_quantity(self):
        # First add an item
        self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )
        cart = Cart.objects.first()
        item = cart.items.first()

        # Update quantity
        response = self.client.post(
            reverse('cart:update_cart', kwargs={'item_id': item.id}),
            {'quantity': 5}
        )
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_update_cart_remove_on_zero(self):
        self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )
        cart = Cart.objects.first()
        item = cart.items.first()

        response = self.client.post(
            reverse('cart:update_cart', kwargs={'item_id': item.id}),
            {'quantity': 0}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_remove_from_cart(self):
        self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )
        cart = Cart.objects.first()
        item = cart.items.first()

        response = self.client.post(
            reverse('cart:remove_from_cart', kwargs={'item_id': item.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_cart_context_processor(self):
        response = self.client.get(reverse('home'))
        self.assertIn('cart_item_count', response.context)


class AuthenticatedCartTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.client.login(username='testuser', password='pass123')
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product", price=29.99, stock=10, category=self.category
        )

    def test_authenticated_add_to_cart(self):
        self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )
        cart = Cart.objects.filter(user=self.user).first()
        self.assertIsNotNone(cart)
        self.assertEqual(cart.items.count(), 1)
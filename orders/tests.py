from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Category, Product
from cart.models import Cart, CartItem
from .models import Order, OrderItem


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.order = Order.objects.create(
            user=self.user,
            full_name="John Doe",
            email="john@example.com",
            address="123 Main St",
            city="New York",
            zip_code="10001",
            total=99.99,
            status='pending'
        )

    def test_order_creation(self):
        self.assertEqual(self.order.full_name, "John Doe")
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.total, 99.99)

    def test_order_str(self):
        self.assertIn("John Doe", str(self.order))

    def test_order_status_choices(self):
        for status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
            self.order.status = status
            self.order.save()
            self.assertEqual(self.order.status, status)

    def test_order_default_status(self):
        order = Order.objects.create(
            user=self.user, full_name="Jane", email="jane@e.com",
            address="456 Oak", city="LA", zip_code="90001", total=50.00
        )
        self.assertEqual(order.status, 'pending')


class OrderItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product", price=49.99, stock=10, category=self.category
        )
        self.order = Order.objects.create(
            user=self.user, full_name="John Doe", email="john@example.com",
            address="123 Main St", city="NY", zip_code="10001", total=99.98
        )
        self.order_item = OrderItem.objects.create(
            order=self.order, product=self.product, price=49.99, quantity=2
        )

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, 49.99)

    def test_order_item_subtotal(self):
        self.assertEqual(self.order_item.subtotal, 99.98)

    def test_order_item_str(self):
        self.assertIn("Test Product", str(self.order_item))


class CheckoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.client.login(username='testuser', password='pass123')
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product", price=29.99, stock=10, category=self.category
        )
        # Create cart with item
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_checkout_get(self):
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)

    def test_checkout_post_success(self):
        data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'address': '123 Main St',
            'city': 'New York',
            'zip_code': '10001',
        }
        response = self.client.post(reverse('orders:checkout'), data)
        self.assertEqual(response.status_code, 302)
        # Verify order was created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        from decimal import Decimal
        self.assertEqual(order.total, Decimal('59.98'))
        self.assertEqual(order.items.count(), 1)
        # Verify stock decremented
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        # Verify cart cleared
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)

    def test_checkout_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_checkout_empty_cart_redirects(self):
        self.cart.items.all().delete()
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 302)


class OrderListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.client.login(username='testuser', password='pass123')

    def test_order_list_status_code(self):
        response = self.client.get(reverse('orders:order_list'))
        self.assertEqual(response.status_code, 200)

    def test_order_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('orders:order_list'))
        self.assertEqual(response.status_code, 302)


class OrderDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        self.client.login(username='testuser', password='pass123')
        self.order = Order.objects.create(
            user=self.user, full_name="John Doe", email="john@example.com",
            address="123 Main St", city="NY", zip_code="10001", total=99.99
        )

    def test_order_detail_status_code(self):
        response = self.client.get(reverse('orders:order_detail', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 200)

    def test_order_detail_shows_total(self):
        response = self.client.get(reverse('orders:order_detail', kwargs={'pk': self.order.pk}))
        self.assertContains(response, "99.99")

    def test_order_detail_other_user_404(self):
        other_user = User.objects.create_user('other', 'other@test.com', 'pass123')
        self.client.login(username='other', password='pass123')
        response = self.client.get(reverse('orders:order_detail', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 404)
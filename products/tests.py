from django.test import TestCase
from django.urls import reverse
from .models import Category, Product


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.slug, "test-category")

    def test_category_str(self):
        self.assertEqual(str(self.category), "Test Category")

    def test_category_auto_slug(self):
        cat = Category.objects.create(name="Another Category")
        self.assertEqual(cat.slug, "another-category")

    def test_category_with_parent(self):
        child = Category.objects.create(name="Sub Category", parent=self.category)
        self.assertEqual(child.parent, self.category)

    def test_get_absolute_url(self):
        url = self.category.get_absolute_url()
        self.assertIn('category=test-category', url)


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Product",
            description="A great product",
            price=99.99,
            stock=10,
            category=self.category,
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.slug, "test-product")
        self.assertEqual(self.product.price, 99.99)
        self.assertEqual(self.product.stock, 10)

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Product")

    def test_in_stock_true(self):
        self.assertTrue(self.product.in_stock)

    def test_in_stock_false(self):
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.in_stock)

    def test_get_absolute_url(self):
        url = self.product.get_absolute_url()
        self.assertIn('test-product', url)

    def test_featured_default_false(self):
        self.assertFalse(self.product.featured)


class HomeViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Featured Product",
            price=49.99,
            stock=5,
            category=self.category,
            featured=True,
        )

    def test_home_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_shows_featured_products(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Featured Product")

    def test_home_shows_categories(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Electronics")


class ProductListViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        for i in range(15):
            Product.objects.create(
                name=f"Product {i}",
                price=10.00 + i,
                stock=10,
                category=self.category,
            )

    def test_product_list_status_code(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_pagination(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(len(response.context['products']), 12)

    def test_product_list_page_2(self):
        response = self.client.get(reverse('products:product_list') + '?page=2')
        self.assertEqual(len(response.context['products']), 3)

    def test_product_list_filter_by_category(self):
        response = self.client.get(reverse('products:product_list') + '?category=electronics')
        # Paginated at 12 per page, so first page has 12
        self.assertEqual(response.context['products'].count(), 12)
        # But total should be 15
        self.assertEqual(response.context['page_obj'].paginator.count, 15)

    def test_product_list_search(self):
        response = self.client.get(reverse('products:product_list') + '?q=Product 5')
        self.assertTrue(response.context['products'].count() >= 1)


class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Detail Product",
            description="Detailed description",
            price=59.99,
            stock=5,
            category=self.category,
        )

    def test_product_detail_status_code(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_product_detail_content(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, "Detail Product")
        self.assertContains(response, "59.99")

    def test_product_detail_404(self):
        response = self.client.get(reverse('products:product_detail', kwargs={'slug': 'nonexistent'}))
        self.assertEqual(response.status_code, 404)
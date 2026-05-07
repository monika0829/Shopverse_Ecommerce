import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Seed the database with sample products and categories'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Ensure media/products directory exists
        media_dir = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'products'
        media_dir.mkdir(parents=True, exist_ok=True)

        # Image mapping: product slug -> fixture image filename
        image_map = {
            'wireless-bluetooth-headphones': 'headphones.jpg',
            'smart-fitness-watch': 'watch.jpg',
            'organic-cotton-t-shirt': 'tshirt.jpg',
            'the-art-of-programming': 'book.jpg',
            'premium-yoga-mat': 'yogamat.jpg',
            'ceramic-coffee-mug-set': 'mug.jpg',
            'portable-bluetooth-speaker': 'speaker.jpg',
            'mechanical-keyboard': 'keyboard.jpg',
            'running-shoes-pro': 'shoes.jpg',
            'minimalist-desk-lamp': 'lamp.jpg',
            'strategy-board-game-collection': 'boardgame.jpg',
            'stainless-steel-water-bottle': 'waterbottle.jpg',
            'wireless-charging-pad': 'charger.jpg',
            'science-fiction-novel-set': 'scifibook.jpg',
            'indoor-plant-kit': 'plant.jpg',
            'leather-journal-notebook': 'journal.jpg',
        }

        fixtures_dir = Path(__file__).resolve().parent.parent / 'fixtures' / 'images'

        # Create categories
        categories_data = {
            'Electronics': {
                'children': ['Smartphones', 'Laptops', 'Headphones'],
            },
            'Clothing': {
                'children': ['Men', 'Women', 'Kids'],
            },
            'Home & Garden': {
                'children': ['Furniture', 'Decor', 'Kitchen'],
            },
            'Books': {
                'children': ['Fiction', 'Non-Fiction', 'Technical'],
            },
            'Sports': {
                'children': ['Fitness', 'Outdoor', 'Team Sports'],
            },
            'Toys & Games': {
                'children': ['Board Games', 'Action Figures', 'Educational'],
            },
        }

        created_categories = {}
        for name, data in categories_data.items():
            cat, created = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name}
            )
            created_categories[name] = cat
            if created:
                self.stdout.write(f'  Created category: {name}')

            for child_name in data.get('children', []):
                child, c = Category.objects.get_or_create(
                    slug=slugify(child_name),
                    defaults={'name': child_name, 'parent': cat}
                )
                if c:
                    self.stdout.write(f'    Created subcategory: {child_name}')

        # Create products
        products_data = [
            {
                'name': 'Wireless Bluetooth Headphones',
                'description': 'Premium noise-cancelling wireless headphones with 30-hour battery life. Features active noise cancellation, comfortable over-ear design, and crystal-clear audio quality.',
                'price': 79.99,
                'stock': 50,
                'category': 'Headphones',
                'featured': True,
                'rating': 4.50,
                'reviews_count': 2341,
            },
            {
                'name': 'Smart Fitness Watch',
                'description': 'Track your health and fitness goals with this advanced smartwatch. Heart rate monitoring, GPS tracking, sleep analysis, and 7-day battery life.',
                'price': 199.99,
                'stock': 30,
                'category': 'Electronics',
                'featured': True,
                'rating': 4.30,
                'reviews_count': 1876,
            },
            {
                'name': 'Organic Cotton T-Shirt',
                'description': 'Comfortable and sustainable 100% organic cotton t-shirt. Available in multiple colors. Soft, breathable, and eco-friendly.',
                'price': 29.99,
                'stock': 200,
                'category': 'Clothing',
                'featured': True,
                'rating': 4.70,
                'reviews_count': 3420,
            },
            {
                'name': 'The Art of Programming',
                'description': 'A comprehensive guide to modern software development practices. Covers algorithms, design patterns, and best practices for writing clean, maintainable code.',
                'price': 39.99,
                'stock': 100,
                'category': 'Books',
                'featured': True,
                'rating': 4.80,
                'reviews_count': 892,
            },
            {
                'name': 'Premium Yoga Mat',
                'description': 'Extra thick, non-slip yoga mat perfect for all types of exercise. Made from eco-friendly TPE material with alignment markings.',
                'price': 49.99,
                'stock': 75,
                'category': 'Sports',
                'featured': True,
                'rating': 4.60,
                'reviews_count': 1567,
            },
            {
                'name': 'Ceramic Coffee Mug Set',
                'description': 'Set of 4 handmade ceramic coffee mugs. Microwave and dishwasher safe. Each holds 12oz. Available in earth tone colors.',
                'price': 34.99,
                'stock': 60,
                'category': 'Kitchen',
                'featured': True,
                'rating': 4.40,
                'reviews_count': 987,
            },
            {
                'name': 'Portable Bluetooth Speaker',
                'description': 'Waterproof portable speaker with 360° surround sound. 12-hour battery life, built-in microphone, and compact design.',
                'price': 59.99,
                'stock': 40,
                'category': 'Electronics',
                'featured': True,
                'rating': 4.20,
                'reviews_count': 2156,
            },
            {
                'name': 'Mechanical Keyboard',
                'description': 'RGB mechanical keyboard with Cherry MX switches. Full-size layout with programmable keys, detachable wrist rest, and USB-C connection.',
                'price': 129.99,
                'stock': 25,
                'category': 'Electronics',
                'featured': True,
                'rating': 4.70,
                'reviews_count': 1432,
            },
            {
                'name': 'Running Shoes Pro',
                'description': 'Lightweight running shoes with responsive cushioning and breathable mesh upper. Perfect for daily training and long-distance running.',
                'price': 119.99,
                'stock': 45,
                'category': 'Sports',
                'featured': False,
                'rating': 4.10,
                'reviews_count': 678,
            },
            {
                'name': 'Minimalist Desk Lamp',
                'description': 'Modern LED desk lamp with adjustable brightness and color temperature. Touch control, USB charging port, and sleek aluminum design.',
                'price': 44.99,
                'stock': 80,
                'category': 'Furniture',
                'featured': False,
                'rating': 4.30,
                'reviews_count': 543,
            },
            {
                'name': 'Strategy Board Game Collection',
                'description': 'Award-winning strategy board game for 2-6 players. Easy to learn, hard to master. Includes 200+ cards, game board, and detailed rulebook.',
                'price': 54.99,
                'stock': 35,
                'category': 'Board Games',
                'featured': False,
                'rating': 4.90,
                'reviews_count': 1234,
            },
            {
                'name': 'Stainless Steel Water Bottle',
                'description': 'Double-wall vacuum insulated water bottle. Keeps drinks cold for 24 hours or hot for 12 hours. BPA-free, leak-proof lid.',
                'price': 24.99,
                'stock': 150,
                'category': 'Sports',
                'featured': False,
                'rating': 4.50,
                'reviews_count': 4521,
            },
            {
                'name': 'Wireless Charging Pad',
                'description': 'Fast wireless charging pad compatible with all Qi-enabled devices. Slim design with LED indicator and built-in safety features.',
                'price': 19.99,
                'stock': 100,
                'category': 'Electronics',
                'featured': False,
                'rating': 4.00,
                'reviews_count': 876,
            },
            {
                'name': 'Science Fiction Novel Set',
                'description': 'Collection of 5 bestselling science fiction novels. Explore distant galaxies, AI civilizations, and time travel adventures.',
                'price': 64.99,
                'stock': 40,
                'category': 'Fiction',
                'featured': False,
                'rating': 4.60,
                'reviews_count': 345,
            },
            {
                'name': 'Indoor Plant Kit',
                'description': 'Complete indoor gardening kit with 3 succulent plants, decorative pots, soil, and care guide. Perfect for beginners.',
                'price': 39.99,
                'stock': 55,
                'category': 'Decor',
                'featured': False,
                'rating': 4.40,
                'reviews_count': 765,
            },
            {
                'name': 'Leather Journal Notebook',
                'description': 'Handcrafted genuine leather journal with 200 pages of acid-free paper. Perfect for writing, sketching, or bullet journaling.',
                'price': 27.99,
                'stock': 90,
                'category': 'Books',
                'featured': False,
                'rating': 4.80,
                'reviews_count': 1102,
            },
        ]

        for product_data in products_data:
            cat_name = product_data.pop('category')
            category = Category.objects.filter(
                name=cat_name
            ).first() or Category.objects.filter(
                children__name=cat_name
            ).first()

            if category is None:
                category = Category.objects.filter(name=cat_name).first()

            slug = slugify(product_data['name'])
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={**product_data, 'category': category}
            )

            if created:
                self.stdout.write(f'  Created product: {product.name}')
            else:
                # Update existing products with new fields
                updated = False
                for field in ['rating', 'reviews_count', 'description', 'price', 'stock', 'featured']:
                    new_val = product_data.get(field)
                    if new_val is not None and getattr(product, field) != new_val:
                        setattr(product, field, new_val)
                        updated = True
                if updated:
                    product.save(update_fields=[f for f in ['rating', 'reviews_count', 'description', 'price', 'stock', 'featured'] if f in product_data])
                    self.stdout.write(f'  Updated product: {product.name}')

            # Assign product image (always try, uses not product.image guard)
            product.refresh_from_db()
            image_filename = image_map.get(slug)
            if image_filename:
                source = fixtures_dir / image_filename
                if source.exists() and not product.image:
                    with open(source, 'rb') as f:
                        product.image.save(image_filename, File(f), save=True)
                    self.stdout.write(f'    Assigned image: {image_filename}')

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
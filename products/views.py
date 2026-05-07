from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView

from .models import Product, Category


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            featured=True, stock__gt=0
        ).select_related('category')[:8]
        context['categories'] = Category.objects.filter(parent__isnull=True)
        return context


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.select_related('category')
        category_slug = self.request.GET.get('category')
        search_query = self.request.GET.get('q')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query) | \
                       queryset.filter(description__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent__isnull=True)
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category
        ).exclude(pk=self.object.pk)[:4]
        return context
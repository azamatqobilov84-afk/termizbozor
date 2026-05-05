from django.shortcuts import render
from django.db.models import Min, Max, Count, Avg
from django.http import JsonResponse
from datetime import date, timedelta
from decimal import Decimal
from apps.products.models import Product, Category
from apps.markets.models import Market
from apps.prices.models import Price


def home(request):
    """Bosh sahifa."""
    recent_date = date.today() - timedelta(days=7)

    # Markets
    markets = Market.objects.filter(is_active=True)
    categories = Category.objects.all()

    # Cheapest products today
    cheapest_today = []
    expensive_today = []
    popular_products = Product.objects.filter(is_active=True, is_popular=True)[:8]

    for product in Product.objects.filter(is_active=True)[:50]:
        prices = Price.objects.filter(
            product=product, date__gte=recent_date
        ).select_related('market').order_by('-date')

        # Get latest price per market
        seen = set()
        unique_prices = []
        for p in prices:
            if p.market_id not in seen:
                unique_prices.append(p)
                seen.add(p.market_id)

        if len(unique_prices) >= 2:
            cheapest = min(unique_prices, key=lambda p: p.price)
            expensive = max(unique_prices, key=lambda p: p.price)
            diff = expensive.price - cheapest.price
            diff_percent = (diff / expensive.price * 100) if expensive.price > 0 else 0

            cheapest_today.append({
                'product': product,
                'cheapest': cheapest,
                'expensive': expensive,
                'diff': diff,
                'diff_percent': diff_percent,
            })

    # Sort by largest savings
    cheapest_today.sort(key=lambda x: x['diff_percent'], reverse=True)
    big_savings = cheapest_today[:8]

    # Statistics
    stats = {
        'markets_count': markets.count(),
        'products_count': Product.objects.filter(is_active=True).count(),
        'prices_today': Price.objects.filter(date=date.today()).count(),
        'prices_week': Price.objects.filter(date__gte=recent_date).count(),
    }

    # Popular products with prices
    popular_with_prices = []
    for product in popular_products:
        prices = Price.objects.filter(
            product=product, date__gte=recent_date
        ).select_related('market').order_by('-date')

        seen = set()
        unique_prices = []
        for p in prices:
            if p.market_id not in seen:
                unique_prices.append(p)
                seen.add(p.market_id)

        if unique_prices:
            cheapest = min(unique_prices, key=lambda p: p.price)
            popular_with_prices.append({
                'product': product,
                'cheapest': cheapest,
                'market_count': len(unique_prices),
            })

    return render(request, 'core/home.html', {
        'markets': markets,
        'categories': categories,
        'big_savings': big_savings,
        'popular_products': popular_with_prices,
        'stats': stats,
    })


def search_api(request):
    """API: mahsulotlarni qidirish (autocomplete uchun)."""
    query = request.GET.get('q', '').strip()
    results = []

    if len(query) >= 2:
        products = Product.objects.filter(
            is_active=True, name__icontains=query
        ).select_related('category')[:10]

        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'icon': product.icon or product.category.icon,
                'category': product.category.name,
                'unit': product.get_unit_display(),
                'url': product.get_absolute_url(),
            })

    return JsonResponse({'results': results})


def about(request):
    """Sayt haqida sahifa."""
    return render(request, 'core/about.html')

from django.shortcuts import render, get_object_or_404
from django.db.models import Min, Max, Avg, Q
from datetime import date, timedelta
from .models import Market
from apps.prices.models import Price
from apps.products.models import Category, Product


def market_list(request):
    """Barcha bozorlar ro'yxati."""
    markets = Market.objects.filter(is_active=True)
    return render(request, 'markets/list.html', {
        'markets': markets,
    })


def market_detail(request, slug):
    """Bozor sahifasi - shu bozordagi barcha mahsulotlar narxi."""
    market = get_object_or_404(Market, slug=slug, is_active=True)

    # Bugungi va oxirgi 7 kunlik narxlar
    recent_date = date.today() - timedelta(days=7)

    category_id = request.GET.get('category')
    search = request.GET.get('q', '').strip()

    # Get latest price for each product in this market
    prices_qs = Price.objects.filter(
        market=market, date__gte=recent_date
    ).select_related('product', 'product__category').order_by('product', '-date')

    # Get latest price per product
    seen_products = set()
    prices = []
    for price in prices_qs:
        if price.product_id not in seen_products:
            if category_id and str(price.product.category_id) != category_id:
                continue
            if search and search.lower() not in price.product.name.lower():
                continue
            prices.append(price)
            seen_products.add(price.product_id)

    # Group by category
    categories = Category.objects.all()
    prices_by_category = {}
    for price in prices:
        cat = price.product.category
        if cat not in prices_by_category:
            prices_by_category[cat] = []
        prices_by_category[cat].append(price)

    return render(request, 'markets/detail.html', {
        'market': market,
        'prices_by_category': prices_by_category,
        'categories': categories,
        'selected_category': category_id,
        'search': search,
        'total_products': len(prices),
    })


def map_view(request):
    """Barcha bozorlarni xaritada ko'rsatish."""
    markets = Market.objects.filter(is_active=True)
    return render(request, 'markets/map.html', {
        'markets': markets,
    })

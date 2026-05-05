from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Min, Max, Q
from datetime import date, timedelta
from .models import Product, Category
from apps.prices.models import Price
from apps.markets.models import Market


def product_list(request):
    """Barcha mahsulotlar ro'yxati."""
    category_slug = request.GET.get('category')
    search = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'name')

    products = Product.objects.filter(is_active=True).select_related('category')

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    if sort == 'name':
        products = products.order_by('name')
    elif sort == 'category':
        products = products.order_by('category__order', 'name')

    # Pagination
    paginator = Paginator(products, 24)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    # Add latest prices to each product
    recent_date = date.today() - timedelta(days=14)
    for product in products_page:
        latest_prices = list(Price.objects.filter(
            product=product, date__gte=recent_date
        ).select_related('market').order_by('market', '-date'))

        # Get latest per market
        seen = set()
        unique_prices = []
        for p in latest_prices:
            if p.market_id not in seen:
                unique_prices.append(p)
                seen.add(p.market_id)

        if unique_prices:
            product.cheapest = min(unique_prices, key=lambda p: p.price)
            product.expensive = max(unique_prices, key=lambda p: p.price)
            product.market_count = len(unique_prices)
        else:
            product.cheapest = None
            product.expensive = None
            product.market_count = 0

    categories = Category.objects.all()

    return render(request, 'products/list.html', {
        'products': products_page,
        'categories': categories,
        'selected_category': category_slug,
        'search': search,
        'sort': sort,
    })


def product_detail(request, slug):
    """Mahsulot solishtirish sahifasi - ENG MUHIM SAHIFA."""
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Oxirgi 30 kunlik narxlar
    recent_date = date.today() - timedelta(days=30)
    all_prices = Price.objects.filter(
        product=product, date__gte=recent_date
    ).select_related('market').order_by('market', '-date')

    # Get latest price per market
    latest_per_market = {}
    for price in all_prices:
        if price.market_id not in latest_per_market:
            latest_per_market[price.market_id] = price

    latest_prices = sorted(latest_per_market.values(), key=lambda p: p.price)

    # Mark cheapest and most expensive
    if latest_prices:
        cheapest = latest_prices[0]
        expensive = latest_prices[-1]
        savings = expensive.price - cheapest.price
        savings_percent = (savings / expensive.price * 100) if expensive.price > 0 else 0
    else:
        cheapest = expensive = None
        savings = 0
        savings_percent = 0

    # Price history for chart (last 30 days)
    history_data = {}
    markets = Market.objects.filter(is_active=True)
    for market in markets:
        market_prices = Price.objects.filter(
            product=product, market=market, date__gte=recent_date
        ).order_by('date')
        history_data[market.name] = {
            'color': market.color,
            'data': [
                {'date': p.date.isoformat(), 'price': float(p.price)}
                for p in market_prices
            ]
        }

    # Related products from same category
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:6]

    return render(request, 'products/detail.html', {
        'product': product,
        'latest_prices': latest_prices,
        'cheapest': cheapest,
        'expensive': expensive,
        'savings': savings,
        'savings_percent': savings_percent,
        'history_data': history_data,
        'related': related,
        'markets': markets,
    })

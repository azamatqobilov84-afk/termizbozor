from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Min, Max, Avg
from datetime import date, timedelta
from decimal import Decimal
from .models import Price
from apps.products.models import Product, Category
from apps.markets.models import Market


def cheapest_finder(request):
    """Aqlli savatcha - eng arzon bozorni topish."""
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()
    markets = Market.objects.filter(is_active=True)

    selected_ids = request.GET.getlist('products')
    quantities = {}
    for pid in selected_ids:
        try:
            quantities[int(pid)] = float(request.GET.get(f'qty_{pid}', '1'))
        except (ValueError, TypeError):
            quantities[int(pid)] = 1.0

    result = None
    if selected_ids:
        try:
            selected_ids_int = [int(x) for x in selected_ids]
        except ValueError:
            selected_ids_int = []

        recent_date = date.today() - timedelta(days=14)

        # For each market, calculate total cost
        market_totals = {}
        product_details = {}

        for market in markets:
            total = Decimal('0')
            items = []
            missing_count = 0

            for pid in selected_ids_int:
                qty = Decimal(str(quantities.get(pid, 1)))
                # Get latest price for this product in this market
                latest_price = Price.objects.filter(
                    product_id=pid, market=market, date__gte=recent_date
                ).order_by('-date').first()

                if latest_price:
                    cost = latest_price.price * qty
                    total += cost
                    items.append({
                        'product': latest_price.product,
                        'qty': qty,
                        'price': latest_price.price,
                        'cost': cost,
                    })
                else:
                    missing_count += 1

            market_totals[market.id] = {
                'market': market,
                'total': total,
                'items': items,
                'missing_count': missing_count,
                'available_count': len(items),
            }

        # Find cheapest
        valid_markets = [m for m in market_totals.values() if m['available_count'] > 0]
        valid_markets.sort(key=lambda x: x['total'])

        # "Smart cart" - eng arzon variant har bir mahsulot uchun
        smart_cart = []
        smart_total = Decimal('0')
        for pid in selected_ids_int:
            qty = Decimal(str(quantities.get(pid, 1)))
            cheapest_price = Price.objects.filter(
                product_id=pid, date__gte=recent_date
            ).select_related('market', 'product').order_by('price').first()
            if cheapest_price:
                cost = cheapest_price.price * qty
                smart_cart.append({
                    'product': cheapest_price.product,
                    'market': cheapest_price.market,
                    'qty': qty,
                    'price': cheapest_price.price,
                    'cost': cost,
                })
                smart_total += cost

        result = {
            'markets': valid_markets,
            'cheapest_market': valid_markets[0] if valid_markets else None,
            'most_expensive_market': valid_markets[-1] if valid_markets else None,
            'smart_cart': smart_cart,
            'smart_total': smart_total,
            'savings': (valid_markets[-1]['total'] - valid_markets[0]['total']) if len(valid_markets) > 1 else 0,
        }

    return render(request, 'prices/cheapest.html', {
        'products': products,
        'categories': categories,
        'selected_ids': [int(x) for x in selected_ids if x.isdigit()],
        'quantities': quantities,
        'result': result,
    })


def price_history(request):
    """Narxlar tarixi grafigi."""
    products = Product.objects.filter(is_active=True)
    markets = Market.objects.filter(is_active=True)

    product_id = request.GET.get('product')
    days = int(request.GET.get('days', 30))

    chart_data = None
    selected_product = None

    if product_id:
        try:
            selected_product = Product.objects.get(id=product_id)
            recent_date = date.today() - timedelta(days=days)

            chart_data = {}
            for market in markets:
                prices = Price.objects.filter(
                    product=selected_product,
                    market=market,
                    date__gte=recent_date
                ).order_by('date')
                chart_data[market.name] = {
                    'color': market.color,
                    'data': [
                        {'date': p.date.isoformat(), 'price': float(p.price)}
                        for p in prices
                    ]
                }
        except Product.DoesNotExist:
            pass

    # Top movers
    recent_date = date.today() - timedelta(days=7)
    old_date = date.today() - timedelta(days=14)

    top_movers = []
    for product in Product.objects.filter(is_active=True)[:50]:
        recent_avg = Price.objects.filter(
            product=product, date__gte=recent_date
        ).aggregate(avg=Avg('price'))['avg']

        old_avg = Price.objects.filter(
            product=product, date__gte=old_date, date__lt=recent_date
        ).aggregate(avg=Avg('price'))['avg']

        if recent_avg and old_avg and old_avg > 0:
            change = ((recent_avg - old_avg) / old_avg) * 100
            top_movers.append({
                'product': product,
                'old_price': old_avg,
                'new_price': recent_avg,
                'change': change,
            })

    top_movers.sort(key=lambda x: abs(x['change']), reverse=True)
    top_movers = top_movers[:10]

    return render(request, 'prices/history.html', {
        'products': products,
        'markets': markets,
        'selected_product': selected_product,
        'chart_data': chart_data,
        'days': days,
        'top_movers': top_movers,
    })

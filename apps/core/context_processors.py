from apps.products.models import Category
from apps.markets.models import Market
from django.conf import settings


def global_context(request):
    """Hamma sahifalarda mavjud bo'lgan kontekst."""
    return {
        'site_name': getattr(settings, 'SITE_NAME', 'Termiz Bozor'),
        'nav_categories': Category.objects.all()[:8],
        'nav_markets': Market.objects.filter(is_active=True),
    }

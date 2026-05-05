"""
Daily price update command.
Usage: python manage.py update_prices_daily
Cron: 0 8 * * * python manage.py update_prices_daily
"""
import random
from datetime import date
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.prices.models import Price
from apps.products.models import Product
from apps.markets.models import Market


class Command(BaseCommand):
    help = 'Bugun uchun narxlarni yangilash (avtomatik tarzda)'

    def handle(self, *args, **options):
        today = date.today()
        products = Product.objects.filter(is_active=True)
        markets = Market.objects.filter(is_active=True)

        updated = 0
        for product in products:
            for market in markets:
                # Avvalgi kun narxidan foydalanamiz
                last_price = Price.objects.filter(
                    product=product, market=market, date__lt=today
                ).order_by('-date').first()

                if not last_price:
                    continue

                # 80% ehtimol bilan ushlab qoladi, 20% ehtimol bilan ±5% o'zgartiradi
                if random.random() < 0.8:
                    new_price = last_price.price
                else:
                    change = random.uniform(-0.05, 0.05)
                    new_price = last_price.price * (Decimal('1') + Decimal(str(change)))
                    new_price = round(new_price / 100) * 100

                Price.objects.update_or_create(
                    product=product, market=market, date=today,
                    defaults={'price': new_price, 'is_verified': True}
                )
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'✅ {today} sanasi uchun {updated} ta narx yangilandi'
        ))

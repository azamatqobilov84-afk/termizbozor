"""
Management command to seed the database with Termiz markets, products, and prices.
Usage: python manage.py seed_data
"""
import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.markets.models import Market
from apps.products.models import Category, Product
from apps.prices.models import Price


# Termiz shahridagi 5 ta yirik bozor (haqiqiy ma'lumotlar asosida)
MARKETS_DATA = [
    {
        'name': 'Termiz Shahar Markaziy Dehqon Bozori',
        'address': 'Termiz sh., Zebiniso ko\'chasi, 1-uy',
        'latitude': 37.2242,
        'longitude': 67.2783,
        'working_hours': '06:00 - 19:00',
        'phone': '+998 76 227 12 34',
        'description': 'Termiz shahridagi eng yirik markaziy bozor. Barcha turdagi oziq-ovqat mahsulotlari, ziravorlar va qishloq xo\'jaligi mahsulotlari mavjud.',
        'color': '#22c55e',
        'order': 1,
    },
    {
        'name': 'Yashil Dunyo Markaziy Dehqon Oziq-ovqat Bozori',
        'address': 'Termiz sh., Navoiy ko\'chasi, 7/7',
        'latitude': 37.2215,
        'longitude': 67.2745,
        'working_hours': '07:00 - 20:00',
        'phone': '+998 90 569 46 81',
        'description': 'Zamonaviy bozor. Yangi va sifatli mahsulotlar, ozodalik va tartib bilan mashhur.',
        'color': '#3b82f6',
        'order': 2,
    },
    {
        'name': 'Surxon Savdo Majmuasi',
        'address': 'Termiz sh., Mustaqillik ko\'chasi, 25-uy',
        'latitude': 37.2270,
        'longitude': 67.2820,
        'working_hours': '08:00 - 21:00',
        'phone': '+998 76 224 56 78',
        'description': 'Yirik savdo majmuasi. Oziq-ovqat va kundalik buyumlar uchun qulay joy.',
        'color': '#f59e0b',
        'order': 3,
    },
    {
        'name': 'Eski Termiz Dehqon Bozori',
        'address': 'Termiz sh., Al-Hakim at-Termiziy ko\'chasi, 18-uy',
        'latitude': 37.2180,
        'longitude': 67.2710,
        'working_hours': '06:00 - 18:00',
        'phone': '+998 76 225 33 22',
        'description': 'An\'anaviy dehqon bozori. Mahalliy fermerlardan to\'g\'ridan-to\'g\'ri arzon narxlar.',
        'color': '#dc2626',
        'order': 4,
    },
    {
        'name': 'Termiz Universal Bozori',
        'address': 'Termiz sh., A. Temur ko\'chasi, 42-uy',
        'latitude': 37.2300,
        'longitude': 67.2880,
        'working_hours': '07:00 - 19:00',
        'phone': '+998 76 226 11 99',
        'description': 'Universal bozor — oziq-ovqat, kiyim-kechak, maishiy buyumlar bir joyda.',
        'color': '#8b5cf6',
        'order': 5,
    },
]


CATEGORIES_DATA = [
    {'name': 'Sabzavotlar', 'icon': '🥬', 'color': '#22c55e', 'order': 1},
    {'name': 'Mevalar', 'icon': '🍎', 'color': '#ef4444', 'order': 2},
    {'name': "Go'sht va baliq", 'icon': '🥩', 'color': '#dc2626', 'order': 3},
    {'name': 'Sut mahsulotlari', 'icon': '🥛', 'color': '#3b82f6', 'order': 4},
    {'name': 'Don va un', 'icon': '🌾', 'color': '#f59e0b', 'order': 5},
    {'name': 'Ziravorlar', 'icon': '🌶️', 'color': '#dc2626', 'order': 6},
    {'name': 'Quruq mevalar', 'icon': '🥜', 'color': '#a16207', 'order': 7},
    {'name': 'Ichimliklar', 'icon': '🥤', 'color': '#0ea5e9', 'order': 8},
]


# Mahsulotlar va ularning haqiqatga yaqin narxlari (so'm/birlik)
# Format: (nomi, kategoriya_index, birlik, emoji, base_price, mavsumiy)
PRODUCTS_DATA = [
    # Sabzavotlar (0)
    ('Pomidor', 0, 'kg', '🍅', 12000, True),
    ('Bodring', 0, 'kg', '🥒', 10000, True),
    ('Kartoshka', 0, 'kg', '🥔', 6500, False),
    ('Piyoz', 0, 'kg', '🧅', 5500, False),
    ('Sabzi', 0, 'kg', '🥕', 7000, False),
    ('Qalampir (achchiq)', 0, 'kg', '🌶️', 18000, True),
    ('Qalampir (shirin)', 0, 'kg', '🫑', 15000, True),
    ('Karam (oq)', 0, 'kg', '🥬', 5000, False),
    ('Karam (qizil)', 0, 'kg', '🥬', 8000, False),
    ('Sarimsoq', 0, 'kg', '🧄', 35000, False),
    ('Baqlajon', 0, 'kg', '🍆', 9000, True),
    ('Qovoq', 0, 'kg', '🎃', 6000, True),
    ('Rediska', 0, "bog'lam", '🌱', 4000, True),
    ('Lavlagi', 0, 'kg', '🍠', 7500, False),
    ("Ko'k piyoz", 0, "bog'lam", '🌿', 3500, True),
    ('Jambil', 0, "bog'lam", '🌿', 3000, True),
    ('Ukrop', 0, "bog'lam", '🌿', 3000, True),
    ('Shivit', 0, "bog'lam", '🌿', 3500, True),

    # Mevalar (1)
    ('Olma (qizil)', 1, 'kg', '🍎', 14000, False),
    ('Olma (yashil)', 1, 'kg', '🍏', 13000, False),
    ('Nok', 1, 'kg', '🍐', 16000, True),
    ('Anor', 1, 'kg', '🍷', 25000, True),
    ('Uzum', 1, 'kg', '🍇', 22000, True),
    ('Shaftoli', 1, 'kg', '🍑', 28000, True),
    ("O'rik", 1, 'kg', '🍑', 24000, True),
    ('Gilos', 1, 'kg', '🍒', 35000, True),
    ('Qovun', 1, 'kg', '🍈', 8000, True),
    ('Tarvuz', 1, 'kg', '🍉', 6000, True),
    ('Banan', 1, 'kg', '🍌', 18000, False),
    ('Apelsin', 1, 'kg', '🍊', 16000, False),
    ('Mandarin', 1, 'kg', '🍊', 14000, False),
    ('Limon', 1, 'kg', '🍋', 22000, False),
    ('Xurmo', 1, 'kg', '🍅', 19000, True),

    # Go'sht-baliq (2)
    ("Mol go'shti", 2, 'kg', '🥩', 95000, False),
    ("Qo'y go'shti", 2, 'kg', '🍖', 110000, False),
    ("Tovuq go'shti", 2, 'kg', '🍗', 38000, False),
    ('Qiyma', 2, 'kg', '🥩', 88000, False),
    ('Jigar', 2, 'kg', '🥩', 70000, False),
    ('Baliq (sazan)', 2, 'kg', '🐟', 45000, False),
    ('Baliq (oq)', 2, 'kg', '🐟', 55000, False),
    ('Tuxum (10 dona)', 2, 'dona', '🥚', 18000, False),

    # Sut mahsulotlari (3)
    ('Sut (1L)', 3, 'litr', '🥛', 12000, False),
    ('Qatiq', 3, 'litr', '🥛', 13000, False),
    ('Smetana', 3, 'kg', '🥄', 38000, False),
    ('Tvorog', 3, 'kg', '🧀', 35000, False),
    ('Qaymoq', 3, 'kg', '🥄', 42000, False),
    ("Sariyog'", 3, 'kg', '🧈', 95000, False),
    ('Pishloq (qatiq)', 3, 'kg', '🧀', 65000, False),
    ('Suzma', 3, 'kg', '🥄', 30000, False),

    # Don/un (4)
    ('Guruch (Lazer)', 4, 'kg', '🌾', 18000, False),
    ('Guruch (Devzira)', 4, 'kg', '🌾', 35000, False),
    ('Un (oliy)', 4, 'kg', '🌾', 7500, False),
    ('Un (1-nav)', 4, 'kg', '🌾', 6500, False),
    ('Makaron', 4, 'kg', '🍝', 12000, False),
    ("No'xat", 4, 'kg', '🌰', 22000, False),
    ('Loviya', 4, 'kg', '🫘', 20000, False),
    ('Mosh', 4, 'kg', '🌰', 25000, False),
    ('Arpa', 4, 'kg', '🌾', 8000, False),
    ('Grechka', 4, 'kg', '🌾', 22000, False),

    # Ziravorlar (5)
    ('Zira', 5, 'kg', '🌶️', 85000, False),
    ('Qora qalampir', 5, 'kg', '⚫', 95000, False),
    ('Tuz', 5, 'kg', '🧂', 3500, False),
    ('Paprika', 5, 'kg', '🌶️', 70000, False),
    ('Dafna bargi', 5, 'kg', '🍃', 120000, False),
    ('Kunjut', 5, 'kg', '🌰', 60000, False),

    # Quruq mevalar (6)
    ('Mayiz (oq)', 6, 'kg', '🟤', 65000, False),
    ('Mayiz (qora)', 6, 'kg', '⚫', 70000, False),
    ('Jiyda', 6, 'kg', '🟤', 55000, False),
    ("Yong'oq (mag\'iz)", 6, 'kg', '🌰', 95000, False),
    ('Bodom', 6, 'kg', '🌰', 110000, False),
    ('Pista', 6, 'kg', '🥜', 130000, False),
    ('Anjir', 6, 'kg', '🟤', 85000, False),

    # Ichimliklar (7)
    ('Mineral suv (1.5L)', 7, 'litr', '💧', 5000, False),
    ("Choy (ko'k)", 7, 'kg', '🍵', 45000, False),
    ('Choy (qora)', 7, 'kg', '🍵', 50000, False),
    ('Kofe (dona)', 7, 'kg', '☕', 180000, False),
]


class Command(BaseCommand):
    help = 'Termiz bozor narxlari saytini ma\'lumotlar bilan to\'ldiradi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Necha kunlik narx tarixi yaratiladi (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Avval mavjud ma\'lumotlarni o\'chirish'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        days = options['days']
        clear = options['clear']

        if clear:
            self.stdout.write(self.style.WARNING('Eski ma\'lumotlarni o\'chirish...'))
            Price.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            Market.objects.all().delete()

        # 1. Bozorlar
        self.stdout.write('Bozorlar yaratilmoqda...')
        markets = []
        for data in MARKETS_DATA:
            market, created = Market.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            markets.append(market)
            status = '✅ Yaratildi' if created else '⚠️ Mavjud'
            self.stdout.write(f"  {status}: {market.name}")

        # 2. Kategoriyalar
        self.stdout.write('\nKategoriyalar yaratilmoqda...')
        categories = []
        for data in CATEGORIES_DATA:
            cat, created = Category.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            categories.append(cat)
            status = '✅' if created else '⚠️'
            self.stdout.write(f"  {status} {cat.icon} {cat.name}")

        # 3. Mahsulotlar
        self.stdout.write('\nMahsulotlar yaratilmoqda...')
        products = []
        for data in PRODUCTS_DATA:
            name, cat_idx, unit, icon, base_price, seasonal = data
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': categories[cat_idx],
                    'unit': unit,
                    'icon': icon,
                    'is_seasonal': seasonal,
                    'is_popular': base_price < 30000 and not seasonal,
                }
            )
            products.append((product, base_price))
            if created:
                self.stdout.write(f"  ✅ {icon} {name}")

        # 4. Narxlar (oxirgi N kun uchun)
        self.stdout.write(f'\nNarxlar yaratilmoqda ({days} kun)...')
        today = date.today()
        prices_created = 0

        for day_offset in range(days, -1, -1):
            current_date = today - timedelta(days=day_offset)

            for product, base_price in products:
                for market in markets:
                    # Har bozorda ozgina farqli narx
                    # Markaziy bozorlar arzonroq, universal qimmatroq
                    market_modifier = {
                        markets[0].id: 0.95,   # Markaziy
                        markets[1].id: 1.00,   # Yashil Dunyo
                        markets[2].id: 1.08,   # Surxon
                        markets[3].id: 0.92,   # Eski Termiz (eng arzon)
                        markets[4].id: 1.12,   # Universal (eng qimmat)
                    }.get(market.id, 1.0)

                    # Vaqtiy o'zgaruvchanlik (har kuni 0-3% farq)
                    daily_variation = random.uniform(-0.03, 0.03)

                    # Trend (kun uzoqlashgani sayin narx ozroq)
                    trend = 1 + (day_offset * 0.001)

                    final_price = base_price * market_modifier * (1 + daily_variation) * trend
                    final_price = round(final_price / 100) * 100  # 100 so'mga yaxlitlash

                    Price.objects.update_or_create(
                        product=product,
                        market=market,
                        date=current_date,
                        defaults={
                            'price': Decimal(str(final_price)),
                            'is_verified': True,
                            'quality': random.choice(['high', 'medium', 'medium', 'high']),
                        }
                    )
                    prices_created += 1

            if day_offset % 5 == 0:
                self.stdout.write(f"  📅 {current_date}: {len(products) * len(markets)} narx")

        self.stdout.write(self.style.SUCCESS(f'\n✅ Barchasi tayyor!'))
        self.stdout.write(f'   • Bozorlar: {len(markets)}')
        self.stdout.write(f'   • Kategoriyalar: {len(categories)}')
        self.stdout.write(f'   • Mahsulotlar: {len(products)}')
        self.stdout.write(f'   • Narxlar: {prices_created}')
        self.stdout.write(self.style.SUCCESS(
            f'\n🚀 Endi `python manage.py runserver` deb ishga tushiring!'
        ))

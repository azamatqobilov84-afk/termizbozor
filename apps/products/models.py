from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    """Mahsulot kategoriyasi."""
    name = models.CharField(max_length=100, unique=True, verbose_name='Nomi')
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(
        max_length=10, default='🛒',
        help_text='Emoji yoki belgi',
        verbose_name='Ikonka'
    )
    color = models.CharField(
        max_length=7, default='#22c55e',
        help_text='Hex rang kodi',
        verbose_name='Rang'
    )
    description = models.TextField(blank=True, verbose_name='Tavsif')
    order = models.IntegerField(default=0, verbose_name='Tartib')

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.icon} {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=False)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Mahsulot."""

    class Unit(models.TextChoices):
        KG = 'kg', 'kg (kilogramm)'
        G = 'g', 'g (gramm)'
        DONA = 'dona', 'dona'
        LITR = 'litr', 'litr'
        BOGLAM = 'boglam', "bog'lam"
        TONNA = 'tonna', 'tonna'
        QUTI = 'quti', 'quti'

    name = models.CharField(max_length=150, verbose_name='Mahsulot nomi')
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Kategoriya'
    )
    unit = models.CharField(
        max_length=20,
        choices=Unit.choices,
        default=Unit.KG,
        verbose_name="O'lchov birligi"
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True, null=True,
        verbose_name='Rasm'
    )
    icon = models.CharField(
        max_length=10, blank=True,
        help_text='Rasm o\'rniga emoji ishlatish (masalan 🍅)',
        verbose_name='Emoji'
    )
    description = models.TextField(blank=True, verbose_name='Tavsif')
    is_seasonal = models.BooleanField(default=False, verbose_name='Mavsumiy')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    is_popular = models.BooleanField(
        default=False,
        verbose_name="Mashhur (bosh sahifada ko'rsatish)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'
        ordering = ['category__order', 'name']

    def __str__(self):
        return f"{self.icon} {self.name}".strip()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=False)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    @property
    def display_unit(self):
        return self.get_unit_display().split(' ')[0]

    def get_latest_prices(self):
        """Hamma bozorlardagi oxirgi narxlar."""
        from apps.prices.models import Price
        from datetime import date, timedelta

        recent_date = date.today() - timedelta(days=14)
        prices = Price.objects.filter(
            product=self, date__gte=recent_date
        ).select_related('market').order_by('market', '-date')

        # Get latest price per market
        result = {}
        for price in prices:
            if price.market_id not in result:
                result[price.market_id] = price
        return list(result.values())

    @property
    def cheapest_price(self):
        prices = self.get_latest_prices()
        if not prices:
            return None
        return min(prices, key=lambda p: p.price)

    @property
    def most_expensive_price(self):
        prices = self.get_latest_prices()
        if not prices:
            return None
        return max(prices, key=lambda p: p.price)

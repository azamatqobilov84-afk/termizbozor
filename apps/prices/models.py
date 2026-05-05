from django.db import models
from django.conf import settings
from django.utils import timezone


class Price(models.Model):
    """Mahsulot narxi - asosiy model."""
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name='Mahsulot'
    )
    market = models.ForeignKey(
        'markets.Market',
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name='Bozor'
    )
    price = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name="Narx (so'm)"
    )
    date = models.DateField(verbose_name='Sana')
    recorded_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Kiritilgan vaqt'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='recorded_prices',
        verbose_name='Kim kiritgan'
    )
    is_verified = models.BooleanField(
        default=True,
        verbose_name='Tasdiqlangan'
    )
    quality = models.CharField(
        max_length=20,
        choices=[
            ('high', 'Yuqori sifat'),
            ('medium', "O'rtacha"),
            ('low', 'Past'),
        ],
        default='medium',
        verbose_name='Sifati'
    )
    notes = models.TextField(blank=True, verbose_name='Izohlar')

    class Meta:
        verbose_name = 'Narx'
        verbose_name_plural = 'Narxlar'
        ordering = ['-date', '-recorded_at']
        unique_together = [('product', 'market', 'date')]
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['product', 'market', '-date']),
            models.Index(fields=['market', '-date']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.market.name}: {self.price:,.0f} so'm ({self.date})"

    @property
    def formatted_price(self):
        return f"{self.price:,.0f}".replace(',', ' ')


class PriceHistory(models.Model):
    """Narx o'zgarishlar tarixi."""
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='price_history'
    )
    market = models.ForeignKey(
        'markets.Market',
        on_delete=models.CASCADE,
        related_name='price_history'
    )
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    change_percent = models.DecimalField(
        max_digits=6, decimal_places=2,
        default=0
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Narx tarixi'
        verbose_name_plural = 'Narx tarixi'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.product.name} ({self.market.name}): {self.old_price} → {self.new_price}"

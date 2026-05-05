from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Market(models.Model):
    """Termiz shahridagi bozorlar."""
    name = models.CharField(max_length=200, verbose_name='Bozor nomi')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    address = models.CharField(max_length=300, verbose_name='Manzil')
    description = models.TextField(blank=True, verbose_name='Tavsif')

    # Geolocation
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        verbose_name='Kenglik (latitude)',
        help_text='Termiz uchun: 37.22 atrofida'
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        verbose_name='Uzunlik (longitude)',
        help_text='Termiz uchun: 67.27 atrofida'
    )

    # Contact
    working_hours = models.CharField(
        max_length=100,
        default='06:00 - 19:00',
        verbose_name='Ish vaqti'
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name='Telefon')

    # Visual
    image = models.ImageField(
        upload_to='markets/',
        blank=True, null=True,
        verbose_name='Bozor rasmi'
    )
    color = models.CharField(
        max_length=7,
        default='#22c55e',
        help_text='Hex rang kodi (masalan #22c55e)',
        verbose_name='Bozor rangi (taqqoslash uchun)'
    )

    # Meta
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    order = models.IntegerField(default=0, verbose_name='Tartib')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bozor'
        verbose_name_plural = 'Bozorlar'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=False)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('markets:detail', kwargs={'slug': self.slug})

    @property
    def total_products(self):
        """Bu bozorda mavjud mahsulotlar soni."""
        from apps.prices.models import Price
        from datetime import date, timedelta
        recent_date = date.today() - timedelta(days=7)
        return Price.objects.filter(
            market=self, date__gte=recent_date
        ).values('product').distinct().count()

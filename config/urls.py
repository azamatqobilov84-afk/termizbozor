"""
Termiz Bozor Narxlari URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('mahsulotlar/', include('apps.products.urls')),
    path('bozorlar/', include('apps.markets.urls')),
    path('narxlar/', include('apps.prices.urls')),
    path('accounts/', include('apps.accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "Termiz Bozor Narxlari — Boshqaruv paneli"
admin.site.site_title = "Termiz Bozor Admin"
admin.site.index_title = "Boshqaruv paneli"

from django.urls import path
from . import views

app_name = 'markets'

urlpatterns = [
    path('', views.market_list, name='list'),
    path('xarita/', views.map_view, name='map'),
    path('<slug:slug>/', views.market_detail, name='detail'),
]

from django.urls import path
from . import views

app_name = 'prices'

urlpatterns = [
    path('eng-arzon/', views.cheapest_finder, name='cheapest'),
    path('tarix/', views.price_history, name='history'),
]

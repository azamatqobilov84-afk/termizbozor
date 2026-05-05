from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('haqida/', views.about, name='about'),
    path('api/search/', views.search_api, name='search_api'),
]

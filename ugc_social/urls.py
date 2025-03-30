from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Social media integration URLs will be added here
    path('', views.social_dashboard, name='dashboard'),
    path('platforms/', views.platforms, name='platforms'),
] 
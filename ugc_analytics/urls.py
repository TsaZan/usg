from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Analytics URLs will be added here
    path('', views.analytics_dashboard, name='dashboard'),
    path('overview/', views.overview, name='overview'),
] 
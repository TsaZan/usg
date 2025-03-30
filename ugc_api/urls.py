from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'ugc_api'

router = DefaultRouter()
# Register your viewsets here

urlpatterns = [
    path('', include(router.urls)),
] 
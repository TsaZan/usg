from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ugc_ai'

router = DefaultRouter()
router.register(r'models', views.AIModelViewSet, basename='ai-model')
router.register(r'analyses', views.ContentAnalysisViewSet, basename='content-analysis')
router.register(r'recommendations', views.ContentRecommendationViewSet, basename='content-recommendation')
router.register(r'detections', views.ContentDetectionViewSet, basename='content-detection')

urlpatterns = [
    path('', include(router.urls)),
] 
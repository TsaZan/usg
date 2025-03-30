from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ugc_api'

router = DefaultRouter()
router.register(r'contents', views.ContentViewSet, basename='content')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'tags', views.TagViewSet, basename='tag')

content_router = DefaultRouter()
content_router.register(r'comments', views.ContentCommentViewSet, basename='content-comment')
content_router.register(r'versions', views.ContentVersionViewSet, basename='content-version')

urlpatterns = [
    path('', include(router.urls)),
    path('contents/<int:content_pk>/', include(content_router.urls)),
] 
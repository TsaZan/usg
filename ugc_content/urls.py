from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Content views
    path('', views.content_list, name='content_list'),
    path('create/', views.content_create, name='content_create'),
    path('<int:pk>/', views.content_detail, name='content_detail'),
    path('<int:pk>/update/', views.content_update, name='content_update'),
    path('<int:pk>/delete/', views.content_delete, name='content_delete'),
    path('<int:pk>/publish/', views.content_publish, name='content_publish'),
    path('<int:pk>/schedule/', views.content_schedule, name='content_schedule'),
    path('<int:pk>/archive/', views.content_archive, name='content_archive'),
    
    # Category views
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Tag views
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:pk>/update/', views.tag_update, name='tag_update'),
    path('tags/<int:pk>/delete/', views.tag_delete, name='tag_delete'),
    
    # AJAX views
    path('ajax/<int:pk>/delete/', views.ajax_delete_content, name='ajax_delete_content'),
    path('ajax/<int:pk>/publish/', views.ajax_publish_content, name='ajax_publish_content'),
] 
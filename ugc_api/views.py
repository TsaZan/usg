from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from .serializers import (
    UserSerializer, ContentSerializer, CategorySerializer,
    TagSerializer, ContentCommentSerializer, ContentVersionSerializer
)
from ugc_content.models import Content, Category, Tag, ContentVersion, ContentComment
from django.contrib.auth import get_user_model

User = get_user_model()

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user

class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'content_type', 'platform', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'engagement_score', 'reach_count']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Content.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        content = self.get_object()
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only staff members can approve content.'},
                status=status.HTTP_403_FORBIDDEN
            )
        content.approve()
        return Response({'status': 'content approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        content = self.get_object()
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only staff members can reject content.'},
                status=status.HTTP_403_FORBIDDEN
            )
        content.reject()
        return Response({'status': 'content rejected'})

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        content = self.get_object()
        if content.status != Content.Status.APPROVED:
            return Response(
                {'detail': 'Content must be approved before publishing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        content.publish()
        return Response({'status': 'content published'})

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        content = self.get_object()
        content.archive()
        return Response({'status': 'content archived'})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class ContentCommentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ContentComment.objects.filter(content_id=self.kwargs['content_pk'])

    def perform_create(self, serializer):
        content = get_object_or_404(Content, pk=self.kwargs['content_pk'])
        serializer.save(user=self.request.user, content=content)

class ContentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContentVersionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ContentVersion.objects.filter(content_id=self.kwargs['content_pk'])

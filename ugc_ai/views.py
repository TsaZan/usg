from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import AIModel, ContentAnalysis, ContentRecommendation, ContentDetection
from .serializers import (
    AIModelSerializer, ContentAnalysisSerializer,
    ContentRecommendationSerializer, ContentDetectionSerializer
)
from .services import AIService
from ugc_content.models import Content
from django.utils import timezone
from .tasks import (
    analyze_content_task,
    generate_recommendations_task,
    detect_content_task
)

class AIModelViewSet(viewsets.ModelViewSet):
    """ViewSet for managing AI models."""
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [IsAuthenticated]

class ContentAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for content analysis."""
    queryset = ContentAnalysis.objects.all()
    serializer_class = ContentAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create a new content analysis request."""
        content_id = request.data.get('content_id')
        if not content_id:
            return Response(
                {'error': 'content_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Start async analysis task
        task = analyze_content_task.delay(content_id)
        
        return Response({
            'message': 'Content analysis started',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get the status of a content analysis task."""
        analysis = self.get_object()
        return Response({
            'status': analysis.status,
            'created_at': analysis.created_at,
            'completed_at': analysis.completed_at
        })

class ContentRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for content recommendations."""
    queryset = ContentRecommendation.objects.all()
    serializer_class = ContentRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Generate new content recommendations."""
        limit = int(request.data.get('limit', 10))
        
        # Start async recommendation generation task
        task = generate_recommendations_task.delay(request.user.id, limit)
        
        return Response({
            'message': 'Recommendation generation started',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['get'])
    def personalized(self, request):
        """Get personalized recommendations for the current user."""
        limit = int(request.query_params.get('limit', 10))
        recommendations = self.queryset.filter(
            user=request.user
        ).order_by('-relevance_score')[:limit]
        
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)

class ContentDetectionViewSet(viewsets.ModelViewSet):
    """ViewSet for content detection."""
    queryset = ContentDetection.objects.all()
    serializer_class = ContentDetectionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create a new content detection request."""
        platform = request.data.get('platform')
        query = request.data.get('query')
        
        if not platform or not query:
            return Response(
                {'error': 'platform and query are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create detection record
        detection = ContentDetection.objects.create(
            user=request.user,
            platform=platform,
            query=query,
            status=ContentDetection.DetectionStatus.PENDING
        )

        # Start async detection task
        task = detect_content_task.delay(detection.id)
        
        return Response({
            'message': 'Content detection started',
            'task_id': task.id,
            'detection_id': detection.id
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get the status of a content detection task."""
        detection = self.get_object()
        return Response({
            'status': detection.status,
            'created_at': detection.created_at,
            'completed_at': detection.completed_at,
            'error_message': detection.error_message
        })

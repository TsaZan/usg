from rest_framework import serializers
from .models import AIModel, ContentAnalysis, ContentRecommendation, ContentDetection
from ugc_content.serializers import ContentSerializer

class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = ('id', 'name', 'model_type', 'description', 'version', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class ContentAnalysisSerializer(serializers.ModelSerializer):
    content = ContentSerializer(read_only=True)
    model = AIModelSerializer(read_only=True)

    class Meta:
        model = ContentAnalysis
        fields = (
            'id', 'content', 'model', 'categories', 'confidence_scores',
            'sentiment_score', 'sentiment_label', 'quality_score',
            'engagement_potential', 'processing_time', 'processed_at',
            'error_message'
        )
        read_only_fields = ('processed_at',)

class ContentRecommendationSerializer(serializers.ModelSerializer):
    content = ContentSerializer(read_only=True)

    class Meta:
        model = ContentRecommendation
        fields = (
            'id', 'user', 'content', 'recommendation_type',
            'relevance_score', 'created_at', 'expires_at',
            'is_viewed', 'viewed_at'
        )
        read_only_fields = ('user', 'created_at', 'viewed_at')

class ContentDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentDetection
        fields = (
            'id', 'user', 'platform', 'query', 'status',
            'results', 'error_message', 'created_at',
            'completed_at'
        )
        read_only_fields = ('user', 'status', 'created_at', 'completed_at')

    def validate_query(self, value):
        """Validate the search query parameters."""
        required_fields = ['keywords', 'date_range']
        if not all(field in value for field in required_fields):
            raise serializers.ValidationError(
                f"Query must include: {', '.join(required_fields)}"
            )
        return value 
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class AIModel(models.Model):
    class ModelType(models.TextChoices):
        CLASSIFIER = 'CLASSIFIER', _('Content Classifier')
        SENTIMENT = 'SENTIMENT', _('Sentiment Analyzer')
        RECOMMENDER = 'RECOMMENDER', _('Content Recommender')
        DETECTOR = 'DETECTOR', _('Content Detector')

    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=20, choices=ModelType.choices)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_model_type_display()})"

class ContentAnalysis(models.Model):
    content = models.OneToOneField('ugc_content.Content', on_delete=models.CASCADE, related_name='analysis')
    model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    
    # Classification results
    categories = models.JSONField(null=True, blank=True)
    confidence_scores = models.JSONField(null=True, blank=True)
    
    # Sentiment analysis
    sentiment_score = models.FloatField(
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        null=True,
        blank=True
    )
    sentiment_label = models.CharField(max_length=20, blank=True)
    
    # Content quality metrics
    quality_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        null=True,
        blank=True
    )
    engagement_potential = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        null=True,
        blank=True
    )
    
    # Additional metadata
    processing_time = models.FloatField(null=True, blank=True)
    processed_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-processed_at']

    def __str__(self):
        return f"Analysis for {self.content.title}"

class ContentRecommendation(models.Model):
    class RecommendationType(models.TextChoices):
        SIMILAR = 'SIMILAR', _('Similar Content')
        TRENDING = 'TRENDING', _('Trending Content')
        PERSONALIZED = 'PERSONALIZED', _('Personalized Recommendation')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    content = models.ForeignKey('ugc_content.Content', on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RecommendationType.choices)
    relevance_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'recommendation_type']),
            models.Index(fields=['created_at', 'expires_at']),
        ]

    def __str__(self):
        return f"{self.get_recommendation_type_display()} for {self.user.username}"

class ContentDetection(models.Model):
    class DetectionStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='detections')
    platform = models.CharField(max_length=50)  # Instagram, TikTok, Facebook
    query = models.JSONField()  # Search criteria
    status = models.CharField(max_length=20, choices=DetectionStatus.choices, default=DetectionStatus.PENDING)
    results = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Content Detection for {self.user.username} on {self.platform}"

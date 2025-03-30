from celery import shared_task
from django.utils import timezone
from .models import ContentAnalysis, ContentRecommendation, ContentDetection
from .services import AIService
from ugc_content.models import Content

@shared_task
def analyze_content_task(content_id: int) -> ContentAnalysis:
    """Analyze content using AI service."""
    try:
        content = Content.objects.get(id=content_id)
        ai_service = AIService()
        analysis = ai_service.analyze_content(content)
        return analysis
    except Exception as e:
        print(f"Error in content analysis task: {str(e)}")
        return None

@shared_task
def generate_recommendations_task(user_id: int, limit: int = 10) -> list:
    """Generate personalized content recommendations."""
    try:
        ai_service = AIService()
        recommendations = ai_service.generate_recommendations(user_id, limit)
        return recommendations
    except Exception as e:
        print(f"Error in recommendation generation task: {str(e)}")
        return []

@shared_task
def detect_content_task(detection_id: int) -> ContentDetection:
    """Process content detection request."""
    try:
        detection = ContentDetection.objects.get(id=detection_id)
        ai_service = AIService()
        
        # Update status to processing
        detection.status = ContentDetection.DetectionStatus.PROCESSING
        detection.save()
        
        # Process the detection
        results = ai_service.detect_content(
            user_id=detection.user_id,
            platform=detection.platform,
            query=detection.query
        )
        
        # Update detection with results
        detection.results = results
        detection.status = ContentDetection.DetectionStatus.COMPLETED
        detection.completed_at = timezone.now()
        detection.save()
        
        return detection
    except Exception as e:
        detection.status = ContentDetection.DetectionStatus.FAILED
        detection.error_message = str(e)
        detection.save()
        return detection

@shared_task
def cleanup_old_analyses_task():
    """Clean up old content analyses."""
    try:
        # Delete analyses older than 30 days
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        ContentAnalysis.objects.filter(created_at__lt=cutoff_date).delete()
    except Exception as e:
        print(f"Error in cleanup task: {str(e)}")

@shared_task
def cleanup_old_recommendations_task():
    """Clean up old content recommendations."""
    try:
        # Delete recommendations older than 7 days
        cutoff_date = timezone.now() - timezone.timedelta(days=7)
        ContentRecommendation.objects.filter(created_at__lt=cutoff_date).delete()
    except Exception as e:
        print(f"Error in cleanup task: {str(e)}") 
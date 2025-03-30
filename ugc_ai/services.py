import os
import time
from typing import Dict, List, Optional
from django.conf import settings
from django.utils import timezone
from .models import AIModel, ContentAnalysis, ContentRecommendation, ContentDetection
from ugc_content.models import Content
from celery import shared_task
import openai
from google.cloud import vision
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class AIService:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.google_vision_api_key = settings.GOOGLE_VISION_API_KEY
        
        # Initialize OpenAI
        openai.api_key = self.openai_api_key
        
        # Initialize Google Vision
        self.vision_client = vision.ImageAnnotatorClient()
        
        # Initialize TF-IDF vectorizer for content similarity
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def analyze_content(self, content: Content) -> ContentAnalysis:
        """Analyze content using AI models."""
        start_time = time.time()
        
        try:
            # Get or create AI model
            model, _ = AIModel.objects.get_or_create(
                name='Content Analyzer v1',
                model_type=AIModel.ModelType.CLASSIFIER,
                defaults={
                    'version': '1.0.0',
                    'description': 'Content classification and analysis model'
                }
            )

            # Perform content analysis
            analysis = ContentAnalysis.objects.create(
                content=content,
                model=model
            )

            # Analyze text content
            text_analysis = self._analyze_text(content.description)
            
            # Analyze media content
            media_analysis = self._analyze_media(content.media_file)
            
            # Combine results
            analysis.categories = self._combine_categories(text_analysis, media_analysis)
            analysis.confidence_scores = self._calculate_confidence_scores(text_analysis, media_analysis)
            
            # Perform sentiment analysis
            sentiment_result = self._analyze_sentiment(content.description)
            analysis.sentiment_score = sentiment_result['score']
            analysis.sentiment_label = sentiment_result['label']
            
            # Calculate quality metrics
            analysis.quality_score = self._calculate_quality_score(content)
            analysis.engagement_potential = self._calculate_engagement_potential(content)
            
            # Record processing time
            analysis.processing_time = time.time() - start_time
            analysis.save()
            
            return analysis

        except Exception as e:
            if 'analysis' in locals():
                analysis.error_message = str(e)
                analysis.save()
            raise

    def _analyze_text(self, text: str) -> Dict:
        """Analyze text content using OpenAI API."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a content analyzer. Analyze the following text and provide categories and confidence scores."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            # Parse the response
            analysis = response.choices[0].message.content
            categories = [cat.strip() for cat in analysis.split(',')]
            
            return {
                'categories': categories,
                'confidence': 0.85  # OpenAI doesn't provide confidence scores directly
            }
        except Exception as e:
            print(f"Error in text analysis: {str(e)}")
            return {
                'categories': ['text', 'content'],
                'confidence': 0.5
            }

    def _analyze_media(self, media_file) -> Dict:
        """Analyze media content using Google Vision API."""
        try:
            # Read the image file
            with open(media_file.path, "rb") as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Perform multiple types of detection
            response = self.vision_client.annotate_image({
                'image': image,
                'features': [
                    {'type_': vision.Feature.Type.LABEL_DETECTION},
                    {'type_': vision.Feature.Type.OBJECT_LOCALIZATION},
                    {'type_': vision.Feature.Type.SAFE_SEARCH_DETECTION}
                ]
            })
            
            # Extract labels and objects
            labels = [label.description for label in response.label_annotations]
            objects = [obj.name for obj in response.localized_object_annotations]
            
            # Combine all detected items
            categories = list(set(labels + objects))
            
            # Calculate confidence score (average of all detections)
            confidences = [label.score for label in response.label_annotations]
            confidence = np.mean(confidences) if confidences else 0.5
            
            return {
                'categories': categories,
                'confidence': float(confidence)
            }
        except Exception as e:
            print(f"Error in media analysis: {str(e)}")
            return {
                'categories': ['image', 'media'],
                'confidence': 0.5
            }

    def _combine_categories(self, text_analysis: Dict, media_analysis: Dict) -> List[str]:
        """Combine categories from text and media analysis."""
        # Implement category combination logic
        return list(set(text_analysis['categories'] + media_analysis['categories']))

    def _calculate_confidence_scores(self, text_analysis: Dict, media_analysis: Dict) -> Dict:
        """Calculate confidence scores for combined analysis."""
        return {
            'text': text_analysis['confidence'],
            'media': media_analysis['confidence'],
            'overall': (text_analysis['confidence'] + media_analysis['confidence']) / 2
        }

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using OpenAI API."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a sentiment analyzer. Analyze the sentiment of the following text and provide a score between -1 and 1, and a label (positive, negative, or neutral)."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            # Parse the response
            result = response.choices[0].message.content
            score = float(result.split(',')[0].strip())
            label = result.split(',')[1].strip().lower()
            
            return {
                'score': score,
                'label': label
            }
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            return {
                'score': 0.0,
                'label': 'neutral'
            }

    def _calculate_quality_score(self, content: Content) -> float:
        """Calculate content quality score based on multiple factors."""
        try:
            # Get content analysis
            analysis = content.analysis
            
            # Calculate base score from various factors
            factors = {
                'sentiment': abs(analysis.sentiment_score) * 20,  # 20% weight
                'engagement': analysis.engagement_potential * 0.4,  # 40% weight
                'confidence': analysis.confidence_scores['overall'] * 40  # 40% weight
            }
            
            # Calculate final score
            quality_score = sum(factors.values())
            
            # Normalize to 0-100 range
            return min(max(quality_score, 0), 100)
        except Exception as e:
            print(f"Error in quality score calculation: {str(e)}")
            return 50.0

    def _calculate_engagement_potential(self, content: Content) -> float:
        """Calculate potential engagement score based on content characteristics."""
        try:
            # Get content analysis
            analysis = content.analysis
            
            # Calculate base score from various factors
            factors = {
                'sentiment': (analysis.sentiment_score + 1) * 25,  # 25% weight
                'confidence': analysis.confidence_scores['overall'] * 25,  # 25% weight
                'category_count': min(len(analysis.categories) * 10, 50)  # 50% weight, max 50 points
            }
            
            # Calculate final score
            engagement_score = sum(factors.values())
            
            # Normalize to 0-100 range
            return min(max(engagement_score, 0), 100)
        except Exception as e:
            print(f"Error in engagement potential calculation: {str(e)}")
            return 50.0

    def generate_recommendations(self, user_id: int, limit: int = 10) -> List[ContentRecommendation]:
        """Generate personalized content recommendations."""
        try:
            # Get user's content history
            user_content = Content.objects.filter(user_id=user_id)
            
            if not user_content.exists():
                return []
            
            # Create TF-IDF matrix of content descriptions
            descriptions = [content.description for content in user_content]
            tfidf_matrix = self.vectorizer.fit_transform(descriptions)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Get top similar content
            recommendations = []
            for i in range(min(limit, len(user_content))):
                similar_indices = similarity_matrix[i].argsort()[-3:][::-1][1:]
                
                for idx in similar_indices:
                    content = user_content[idx]
                    recommendation = ContentRecommendation.objects.create(
                        user_id=user_id,
                        content=content,
                        recommendation_type=ContentRecommendation.RecommendationType.SIMILAR,
                        relevance_score=float(similarity_matrix[i][idx])
                    )
                    recommendations.append(recommendation)
            
            return recommendations[:limit]
        except Exception as e:
            print(f"Error in recommendation generation: {str(e)}")
            return []

    def detect_content(self, user_id: int, platform: str, query: Dict) -> ContentDetection:
        """Detect content based on search criteria."""
        detection = ContentDetection.objects.create(
            user_id=user_id,
            platform=platform,
            query=query,
            status=ContentDetection.DetectionStatus.PROCESSING
        )
        
        # Start async task for content detection
        detect_content_task.delay(detection.id)
        
        return detection

@shared_task
def detect_content_task(detection_id: int):
    """Async task for content detection."""
    detection = ContentDetection.objects.get(id=detection_id)
    try:
        # Implement platform-specific content detection
        platform = detection.platform
        query = detection.query
        
        # This is a placeholder for actual platform API integration
        results = {
            'platform': platform,
            'query': query,
            'matches': []
        }
        
        detection.results = results
        detection.status = ContentDetection.DetectionStatus.COMPLETED
        detection.completed_at = timezone.now()
        detection.save()
    except Exception as e:
        detection.status = ContentDetection.DetectionStatus.FAILED
        detection.error_message = str(e)
        detection.save() 
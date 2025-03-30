from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Content(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PENDING = 'PENDING', _('Pending Review')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
        PUBLISHED = 'PUBLISHED', _('Published')
        ARCHIVED = 'ARCHIVED', _('Archived')

    class ContentType(models.TextChoices):
        POST = 'POST', _('Social Media Post')
        STORY = 'STORY', _('Story')
        REEL = 'REEL', _('Reel')
        VIDEO = 'VIDEO', _('Video')
        IMAGE = 'IMAGE', _('Image')
        CAROUSEL = 'CAROUSEL', _('Carousel')

    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=ContentType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    # Relationships
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contents')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    # Media
    media_file = models.FileField(upload_to='content_media/')
    thumbnail = models.ImageField(upload_to='content_thumbnails/', null=True, blank=True)
    
    # Social Media
    platform = models.CharField(max_length=50)  # Instagram, TikTok, Facebook
    original_url = models.URLField(blank=True)
    social_media_id = models.CharField(max_length=100, blank=True)
    
    # Analytics
    engagement_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        null=True,
        blank=True
    )
    reach_count = models.PositiveIntegerField(default=0)
    engagement_count = models.PositiveIntegerField(default=0)
    
    # AI Analysis
    ai_classification = models.JSONField(null=True, blank=True)
    sentiment_score = models.FloatField(
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        null=True,
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'content_type']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['platform', 'social_media_id']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def approve(self):
        self.status = self.Status.APPROVED
        self.save()

    def reject(self):
        self.status = self.Status.REJECTED
        self.save()

    def publish(self):
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.save()

    def archive(self):
        self.status = self.Status.ARCHIVED
        self.save()

class ContentVersion(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    changes = models.JSONField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['content', 'version_number']
        ordering = ['-version_number']

    def __str__(self):
        return f"Version {self.version_number} of {self.content.title}"

class ContentComment(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.content.title}"

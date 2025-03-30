from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

class ContentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Content Categories'

    def __str__(self):
        return self.name

class ContentTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Content(models.Model):
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('facebook', 'Facebook'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = models.TextField()
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(ContentCategory, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(ContentTag, blank=True)
    media_file = models.FileField(upload_to='content/media/', null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    published_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('content:content_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
        super().save(*args, **kwargs)

    def publish(self):
        self.status = 'published'
        self.published_date = timezone.now()
        self.save()

    def schedule(self, date):
        self.status = 'scheduled'
        self.scheduled_date = date
        self.save()

    def archive(self):
        self.status = 'archived'
        self.save()

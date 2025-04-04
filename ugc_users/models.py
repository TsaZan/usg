from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)  # Superusers are automatically verified
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        MANAGER = 'MANAGER', _('Content Manager')
        ANALYST = 'ANALYST', _('Content Analyst')
        USER = 'USER', _('Regular User')

    # Custom fields
    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.USER
    )
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    company = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    
    # Social media integration fields
    instagram_token = models.CharField(max_length=255, blank=True)
    tiktok_token = models.CharField(max_length=255, blank=True)
    facebook_token = models.CharField(max_length=255, blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    content_approval_required = models.BooleanField(default=True)
    
    # Analytics
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    
    # User fields
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(_('verified'), default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def send_verification_email(self):
        """Send verification email to user."""
        if not self.email_verification_token:
            self.email_verification_token = get_random_string(length=32)
            self.email_verification_sent_at = timezone.now()
            self.save()

        subject = 'Verify your email address'
        verification_url = f"{settings.SITE_URL}/users/verify-email/{self.email_verification_token}/"
        
        context = {
            'user': self,
            'verification_url': verification_url,
            'site_name': settings.SITE_NAME,
        }
        
        html_message = render_to_string('users/email/verify_email.html', context)
        plain_message = render_to_string('users/email/verify_email.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            html_message=html_message,
        )

    def verify_email(self, token):
        """Verify user's email with the provided token."""
        if (self.email_verification_token == token and 
            self.email_verification_sent_at and 
            (timezone.now() - self.email_verification_sent_at).days < 7):
            self.is_verified = True
            self.email_verification_token = ''
            self.email_verification_sent_at = None
            self.save()
            return True
        return False

    def has_social_media_connected(self):
        """Check if user has connected any social media accounts"""
        return bool(self.instagram_token or self.tiktok_token or self.facebook_token)
        
    def get_social_media_connections(self):
        """Return list of connected social media platforms"""
        connections = []
        if self.instagram_token:
            connections.append('instagram')
        if self.tiktok_token:
            connections.append('tiktok')
        if self.facebook_token:
            connections.append('facebook')
        return connections

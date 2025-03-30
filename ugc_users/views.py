from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.db import IntegrityError
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import Http404
from django.utils import timezone
from .models import User
from .forms import UserRegistrationForm, UserProfileForm, ProfileUpdateForm
from .decorators import user_verified
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                logger.info(f"New user registered: {user.email}")
                messages.success(request, 'Account created successfully. Please log in.')
                return redirect('users:login')
            else:
                logger.warning(f"Registration form validation failed: {form.errors}")
        except IntegrityError as e:
            logger.error(f"Database integrity error during registration: {str(e)}")
            messages.error(request, 'An error occurred during registration. Please try again.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    try:
        return render(request, 'users/profile.html')
    except Exception as e:
        logger.error(f"Error accessing profile: {str(e)}")
        raise Http404("Profile not found")

@login_required
def profile_edit(request):
    """Edit user profile."""
    return render(request, 'users/profile_edit.html')

@login_required
def settings_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        try:
            if form.is_valid():
                user = form.save()
                logger.info(f"User profile updated: {user.email}")
                messages.success(request, 'Profile updated successfully.')
                return redirect('users:profile')
            else:
                logger.warning(f"Profile update validation failed: {form.errors}")
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            messages.error(request, 'An error occurred while updating your profile.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'users/settings.html', {'form': form})

class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        user.send_verification_email()
        messages.success(self.request, 'Registration successful. Please check your email to verify your account.')
        logger.info(f"New user registered: {user.email}")
        return response

class UserLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """
        Security check complete. Log the user in.
        Handle both email and verification checks.
        """
        user = form.get_user()
        
        # Check if the user exists and is active
        if not user or not user.is_active:
            form.add_error(None, 'Invalid email or password')
            return self.form_invalid(form)
            
        # For superusers and staff, bypass verification check
        if user.is_superuser or user.is_staff:
            return super().form_valid(form)
            
        # For regular users, check verification
        if not user.is_verified:
            messages.warning(self.request, 'Please verify your email address to log in.')
            return redirect('users:login')
            
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        # Get the next URL from the request if it exists
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
            
        # Default redirect to content dashboard for all users
        return reverse('content:dashboard')

class UserLogoutView(LogoutView):
    next_page = 'users:login'

class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f"User profile updated: {self.object.email}")
        messages.success(self.request, 'Profile updated successfully.')
        return response

def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        if user.verify_email(token):
            messages.success(request, 'Email verified successfully. You can now log in.')
            return redirect('users:login')
        else:
            messages.error(request, 'Invalid or expired verification link.')
            return redirect('users:login')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('users:login')

@login_required
def resend_verification_email(request):
    if not request.user.is_verified:
        request.user.send_verification_email()
        messages.success(request, 'Verification email has been resent. Please check your inbox.')
    return redirect('users:profile')

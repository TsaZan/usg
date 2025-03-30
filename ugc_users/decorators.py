from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

def user_verified(function):
    """
    Decorator to check if a user is verified.
    If not verified, redirects to profile page with a message.
    """
    def check_verification(user):
        if not user.is_verified:
            messages.warning(user.request, 'Please verify your email address to access this feature.')
            return False
        return True

    actual_decorator = user_passes_test(check_verification)
    return actual_decorator(function) 
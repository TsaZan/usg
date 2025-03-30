from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def social_dashboard(request):
    """Display social media dashboard."""
    return render(request, 'social/dashboard.html')

@login_required
def platforms(request):
    return render(request, 'social/platforms.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from ugc_content.models import Content

# Create your views here.

@login_required
def analytics_dashboard(request):
    # Get user's content
    user_content = Content.objects.filter(author=request.user)
    
    # Calculate basic metrics
    total_views = 0  # This would come from your analytics tracking system
    total_engagement = 0  # This would come from your analytics tracking system
    total_content = user_content.count()
    
    # Calculate average engagement rate
    avg_engagement_rate = 0  # This would be calculated based on your engagement metrics
    
    # Get platform distribution
    platform_stats = user_content.values('platform').annotate(count=Count('id'))
    platform_labels = [stat['platform'] for stat in platform_stats]
    platform_data = [stat['count'] for stat in platform_stats]
    
    # Get engagement over time (last 7 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    engagement_data = [0] * 7  # Placeholder for actual engagement data
    engagement_labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    
    # Get top performing content
    top_content = user_content.order_by('-published_date')[:5]  # This would be based on actual performance metrics
    
    context = {
        'total_views': total_views,
        'total_engagement': total_engagement,
        'total_content': total_content,
        'avg_engagement_rate': avg_engagement_rate,
        'platform_labels': platform_labels,
        'platform_data': platform_data,
        'engagement_labels': engagement_labels,
        'engagement_data': engagement_data,
        'top_content': top_content,
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def overview(request):
    return render(request, 'analytics/overview.html')

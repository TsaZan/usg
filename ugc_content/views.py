from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Content, ContentCategory, ContentTag
from .forms import ContentForm, ContentCategoryForm, ContentTagForm
from django.utils import timezone

@login_required
def dashboard(request):
    """Dashboard view showing content overview and statistics."""
    # Get user's content
    user_content = Content.objects.filter(author=request.user)
    
    # Get statistics
    total_content = user_content.count()
    draft_content = user_content.filter(status='draft').count()
    scheduled_content = user_content.filter(status='scheduled').count()
    published_content = user_content.filter(status='published').count()
    
    # Get recent content
    recent_content = user_content.order_by('-created_at')[:5]
    
    # Get content by platform
    platform_stats = {
        platform: user_content.filter(platform=platform).count()
        for platform, _ in Content.PLATFORM_CHOICES
    }
    
    # Get content by category
    category_stats = ContentCategory.objects.annotate(
        content_count=Count('content')
    ).values('name', 'content_count')
    
    # Get upcoming scheduled content
    upcoming_content = user_content.filter(
        status='scheduled',
        scheduled_date__gte=timezone.now()
    ).order_by('scheduled_date')[:5]
    
    # Get recent analytics
    recent_analytics = {
        'total_views': 0,
        'total_engagement': 0,
        'top_performing_content': []
    }
    
    context = {
        'total_content': total_content,
        'draft_content': draft_content,
        'scheduled_content': scheduled_content,
        'published_content': published_content,
        'recent_content': recent_content,
        'platform_stats': platform_stats,
        'category_stats': category_stats,
        'upcoming_content': upcoming_content,
        'recent_analytics': recent_analytics,
    }
    return render(request, 'content/dashboard.html', context)

# Create your views here.

@login_required
def content_list(request):
    contents = Content.objects.filter(author=request.user)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        contents = contents.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        contents = contents.filter(status=status)
    
    # Filter by platform
    platform = request.GET.get('platform')
    if platform:
        contents = contents.filter(platform=platform)
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        contents = contents.filter(category_id=category)
    
    # Pagination
    paginator = Paginator(contents, 10)
    page = request.GET.get('page')
    contents = paginator.get_page(page)
    
    context = {
        'contents': contents,
        'categories': ContentCategory.objects.all(),
        'platforms': dict(Content.PLATFORM_CHOICES),
        'statuses': dict(Content.STATUS_CHOICES),
    }
    return render(request, 'content/content_list.html', context)

@login_required
def content_create(request):
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.author = request.user
            content.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Content created successfully!')
            return redirect('content:content_detail', pk=content.pk)
    else:
        form = ContentForm()
    
    return render(request, 'content/content_form.html', {'form': form})

@login_required
def content_detail(request, pk):
    content = get_object_or_404(Content, pk=pk, author=request.user)
    return render(request, 'content/content_detail.html', {'content': content})

@login_required
def content_update(request, pk):
    content = get_object_or_404(Content, pk=pk, author=request.user)
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Content updated successfully!')
            return redirect('content:content_detail', pk=content.pk)
    else:
        form = ContentForm(instance=content)
    
    return render(request, 'content/content_form.html', {'form': form, 'content': content})

@login_required
def content_delete(request, pk):
    content = get_object_or_404(Content, pk=pk, author=request.user)
    if request.method == 'POST':
        content.delete()
        messages.success(request, 'Content deleted successfully!')
        return redirect('content:content_list')
    
    return render(request, 'content/content_confirm_delete.html', {'content': content})

@login_required
def content_publish(request, pk):
    content = get_object_or_404(Content, pk=pk, author=request.user)
    if request.method == 'POST':
        content.publish()
        messages.success(request, 'Content published successfully!')
        return redirect('content:content_detail', pk=content.pk)
    
    return render(request, 'content/content_confirm_publish.html', {'content': content})

@login_required
def content_schedule(request, pk):
    content = get_object_or_404(Content, pk=pk, author=request.user)
    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            content = form.save(commit=False)
            content.schedule(content.scheduled_date)
            messages.success(request, 'Content scheduled successfully!')
            return redirect('content:content_detail', pk=content.pk)
    else:
        form = ContentForm(instance=content)
    
    return render(request, 'content/content_schedule.html', {'form': form, 'content': content})

@login_required
def content_archive(request, pk):
    content = get_object_or_404(Content, pk=pk, author=request.user)
    if request.method == 'POST':
        content.archive()
        messages.success(request, 'Content archived successfully!')
        return redirect('content:content_detail', pk=content.pk)
    
    return render(request, 'content/content_confirm_archive.html', {'content': content})

@login_required
def category_list(request):
    categories = ContentCategory.objects.all()
    return render(request, 'content/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = ContentCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('content:category_list')
    else:
        form = ContentCategoryForm()
    
    return render(request, 'content/category_form.html', {'form': form})

@login_required
def category_update(request, pk):
    category = get_object_or_404(ContentCategory, pk=pk)
    if request.method == 'POST':
        form = ContentCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('content:category_list')
    else:
        form = ContentCategoryForm(instance=category)
    
    return render(request, 'content/category_form.html', {'form': form, 'category': category})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(ContentCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('content:category_list')
    
    return render(request, 'content/category_confirm_delete.html', {'category': category})

@login_required
def tag_list(request):
    tags = ContentTag.objects.all()
    return render(request, 'content/tag_list.html', {'tags': tags})

@login_required
def tag_create(request):
    if request.method == 'POST':
        form = ContentTagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tag created successfully!')
            return redirect('content:tag_list')
    else:
        form = ContentTagForm()
    
    return render(request, 'content/tag_form.html', {'form': form})

@login_required
def tag_update(request, pk):
    tag = get_object_or_404(ContentTag, pk=pk)
    if request.method == 'POST':
        form = ContentTagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tag updated successfully!')
            return redirect('content:tag_list')
    else:
        form = ContentTagForm(instance=tag)
    
    return render(request, 'content/tag_form.html', {'form': form, 'tag': tag})

@login_required
def tag_delete(request, pk):
    tag = get_object_or_404(ContentTag, pk=pk)
    if request.method == 'POST':
        tag.delete()
        messages.success(request, 'Tag deleted successfully!')
        return redirect('content:tag_list')
    
    return render(request, 'content/tag_confirm_delete.html', {'tag': tag})

@require_POST
@login_required
def ajax_delete_content(request, pk):
    content = get_object_or_404(Content, pk=pk, author=request.user)
    content.delete()
    return JsonResponse({'status': 'success'})

@require_POST
@login_required
def ajax_publish_content(request, pk):
    content = get_object_or_404(Content, pk=pk, author=request.user)
    content.publish()
    return JsonResponse({'status': 'success'})

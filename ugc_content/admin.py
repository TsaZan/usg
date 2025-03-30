from django.contrib import admin
from django.utils.html import format_html
from .models import Content, Tag, Category

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'platform', 'status', 'created_at', 'scheduled_for', 'published_at')
    list_filter = ('status', 'platform', 'content_type', 'category', 'tags', 'created_at')
    search_fields = ('title', 'description', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'content_type', 'platform', 'status')
        }),
        ('Media', {
            'fields': ('media_file', 'thumbnail')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Scheduling', {
            'fields': ('scheduled_for',)
        }),
        ('User Information', {
            'fields': ('user',)
        }),
        ('Social Media', {
            'fields': ('original_url', 'social_media_id')
        }),
        ('Analytics', {
            'fields': ('engagement_score', 'reach_count', 'engagement_count')
        }),
        ('AI Analysis', {
            'fields': ('ai_classification', 'sentiment_score')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ('tags',)
    raw_id_fields = ('user', 'category')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new content
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

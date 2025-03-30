from django.contrib import admin
from django.utils.html import format_html
from .models import Content, ContentCategory, ContentTag

@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(ContentTag)
class ContentTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'platform', 'status', 'created_at', 'scheduled_date', 'published_date')
    list_filter = ('status', 'platform', 'category', 'tags', 'created_at', 'scheduled_date', 'published_date')
    search_fields = ('title', 'description', 'content', 'author__username', 'author__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'published_date')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'content', 'platform', 'status')
        }),
        ('Media', {
            'fields': ('media_file',)
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date',)
        }),
        ('Author Information', {
            'fields': ('author',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_date'),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ('tags',)
    raw_id_fields = ('author', 'category')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new content
            obj.author = request.user
        super().save_model(request, obj, form, change)

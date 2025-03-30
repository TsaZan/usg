from rest_framework import serializers
from django.contrib.auth import get_user_model
from ugc_content.models import Content, Category, Tag, ContentVersion, ContentComment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 
                 'bio', 'company', 'position', 'profile_picture')
        read_only_fields = ('id',)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')

class ContentCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ContentComment
        fields = ('id', 'user', 'text', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class ContentVersionSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = ContentVersion
        fields = ('id', 'version_number', 'changes', 'created_by', 'created_at')
        read_only_fields = ('created_at',)

class ContentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = ContentCommentSerializer(many=True, read_only=True)
    versions = ContentVersionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Content
        fields = (
            'id', 'title', 'description', 'content_type', 'status',
            'user', 'category', 'tags', 'media_file', 'thumbnail',
            'platform', 'original_url', 'social_media_id',
            'engagement_score', 'reach_count', 'engagement_count',
            'ai_classification', 'sentiment_score',
            'created_at', 'updated_at', 'scheduled_for', 'published_at',
            'comments', 'versions'
        )
        read_only_fields = ('created_at', 'updated_at', 'published_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Create a new version if significant changes are made
        if any(key in validated_data for key in ['title', 'description', 'content_type']):
            version_number = instance.versions.count() + 1
            ContentVersion.objects.create(
                content=instance,
                version_number=version_number,
                changes=validated_data,
                created_by=self.context['request'].user
            )
        return super().update(instance, validated_data) 
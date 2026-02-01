from rest_framework import serializers
from .models import Engagement, Like, Comment
from users.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'engagement', 'author', 'author_email', 'content', 'created_at', 'parent', 'replies')
        read_only_fields = ('engagement', 'author')

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'user', 'created_at')

class EngagementSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Engagement
        fields = ('id', 'photo', 'likes_count', 'comments')

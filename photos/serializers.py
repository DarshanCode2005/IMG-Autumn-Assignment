from rest_framework import serializers
from .models import Photo, TaggedIn
from users.serializers import UserSerializer

class TaggedInSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TaggedIn
        fields = ('id', 'user', 'created_at')

class PhotoSerializer(serializers.ModelSerializer):
    uploader = UserSerializer(read_only=True)
    tagged_users = TaggedInSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = '__all__'
        read_only_fields = ('uploader', 'processing_status', 'created_at', 'exif_data', 'ai_tags')

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_comments_count(self, obj):
        if hasattr(obj, 'engagement'):
            return obj.engagement.comments.count()
        return 0

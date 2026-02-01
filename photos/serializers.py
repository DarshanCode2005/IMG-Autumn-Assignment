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
    
    class Meta:
        model = Photo
        fields = '__all__'
        read_only_fields = ('uploader', 'processing_status', 'created_at', 'exif_data', 'ai_tags')

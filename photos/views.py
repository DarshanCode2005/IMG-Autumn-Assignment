from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Photo, TaggedIn
from .serializers import PhotoSerializer
from rest_framework.decorators import action
from social.models import Like, Engagement, Comment
from social.serializers import CommentSerializer

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-created_at')
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    filterset_fields = ['event']

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        files = request.FILES.getlist('files')
        event_id = request.data.get('event_id')
        
        created_photos = []
        for file in files:
            data = {'original_image': file}
            if event_id:
                data['event'] = event_id
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                photo_instance = serializer.save(uploader=request.user)
                created_photos.append(serializer.data)
                
                # Trigger background processing
                from .tasks import process_photo_task
                process_photo_task.delay(photo_instance.id, photo_instance.original_image.path)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(created_photos, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        photo = self.get_object()
        user = request.user
        
        existing_like = Like.objects.filter(photo=photo, user=user).first()
        if existing_like:
            existing_like.delete()
            liked = False
        else:
            Like.objects.create(photo=photo, user=user)
            liked = True
            
        return Response({'liked': liked, 'likes_count': photo.likes.count()})

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        photo = self.get_object()
        
        # Get or create engagement for this photo
        engagement, _ = Engagement.objects.get_or_create(photo=photo)
        
        if request.method == 'GET':
            # Return all top-level comments (with nested replies via serializer)
            comments = Comment.objects.filter(engagement=engagement, parent__isnull=True).order_by('created_at')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Create a new comment
            content = request.data.get('content')
            parent_id = request.data.get('parent_id')
            
            if not content:
                return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            parent = None
            if parent_id:
                try:
                    parent = Comment.objects.get(id=parent_id, engagement=engagement)
                except Comment.DoesNotExist:
                    return Response({'error': 'Parent comment not found'}, status=status.HTTP_404_NOT_FOUND)
            
            comment = Comment.objects.create(
                engagement=engagement,
                author=request.user,
                content=content,
                parent=parent
            )
            
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def tag_user(self, request, pk=None):
        """Tag a user in a photo."""
        photo = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already tagged
        existing_tag = TaggedIn.objects.filter(photo=photo, user=user).first()
        if existing_tag:
            return Response({'message': 'User already tagged'}, status=status.HTTP_200_OK)
        
        TaggedIn.objects.create(photo=photo, user=user, tagged_by=request.user)
        return Response({'message': f'User {user.username} tagged successfully'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def tagged_users(self, request, pk=None):
        """Get all users tagged in a photo."""
        photo = self.get_object()
        tags = TaggedIn.objects.filter(photo=photo).select_related('user')
        
        users = [{'id': tag.user.id, 'username': tag.user.username, 'email': tag.user.email} for tag in tags]
        return Response(users)

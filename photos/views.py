from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Photo
from .serializers import PhotoSerializer

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().order_by('-created_at')
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

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
                serializer.save(uploader=request.user)
                created_photos.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(created_photos, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        photo = self.get_object()
        user = request.user
        
        # Check if already liked via Social app models
        from social.models import Like
        
        existing_like = Like.objects.filter(photo=photo, user=user).first()
        if existing_like:
            existing_like.delete()
            liked = False
        else:
            Like.objects.create(photo=photo, user=user)
            liked = True
            
        return Response({'liked': liked, 'likes_count': photo.likes.count()})

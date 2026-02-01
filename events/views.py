from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Event
from .serializers import EventSerializer

class IsAdminOrCoordinatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins and coordinators to create/edit/delete.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admin/coordinator
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'coordinator']

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrCoordinatorOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

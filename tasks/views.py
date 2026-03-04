from rest_framework import viewsets, permissions
from .models import Task
from .serializers import TaskSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission for tasks.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user or request.user.is_staff

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['completed']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

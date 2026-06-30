from rest_framework import viewsets, permissions

from users.models import Rule
from .serializers import RuleSerializer


class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

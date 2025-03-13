from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Issue
from .serializers import IssueSerializer
from .permissions import IsMunicipalOrReadOnly, IsMunicipalUser
from rest_framework.generics import ListAPIView

class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()
    permission_classes = [IsAuthenticated, IsMunicipalOrReadOnly]

    def perform_create(self, serializer):
        # Save the issue with the current user as the reporter.
        serializer.save(reported_by=self.request.user)

# New view for municipal dashboard listing all issues paginated.
class MunicipalIssueListView(ListAPIView):
    queryset = Issue.objects.all().order_by('-priority')
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsMunicipalUser]
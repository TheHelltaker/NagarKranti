from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IssueViewSet, IssueImageViewSet

# Set up the router for ViewSets
router = DefaultRouter()
router.register(r'', IssueViewSet)
router.register(r'images', IssueImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
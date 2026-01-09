from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContentViewSet, CommentViewSet, CosmicEventViewSet,
    RegisterView, LoginView, LogoutView, UserProfileView,
    ProfileUpdateView, AvatarUploadView, ChangePasswordView,
    get_current_user
)
# from .views import api_login, api_logout, api_register

router = DefaultRouter()
router.register(r'content', ContentViewSet, basename='content')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'events', CosmicEventViewSet, basename='event')


# urlpatterns = [
#     path('', include(router.urls)),
#     path('register/', RegisterView.as_view(), name='register'),  # Keep only DRF version
#     path('login/', LoginView.as_view(), name='login'),           # Keep only DRF version  
#     path('logout/', LogoutView.as_view(), name='logout'),        # Keep only DRF version
#     path('profile/', UserProfileView.as_view(), name='api_profile'),  # API endpoint for profile data
# ]

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='api_profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/avatar/', AvatarUploadView.as_view(), name='avatar_upload'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('current-user/', get_current_user, name='current_user'),
]
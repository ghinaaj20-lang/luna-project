from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
import uuid
from .models import Content, Like, Comment, CosmicEvent, UserProfile
from .serializers import (
    ContentSerializer, CommentSerializer, LikeSerializer,
    CosmicEventSerializer, RegisterSerializer, UserSerializer,
    UserProfileSerializer, UserProfileUpdateSerializer
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

@api_view(['GET'])
def get_current_user(request):
    """Get current user data"""
    if request.user.is_authenticated:
        user = request.user
        try:
            profile = UserProfile.objects.get(user=user)
            profile_data = UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            profile_data = {
                'bio': '',
                'location': '',
                'profile_picture': None,
                'join_date': None
            }
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined
            },
            'profile': profile_data
        })
    return Response({'error': 'Not authenticated'}, status=401)

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'email': user.email
                    }
                })
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

@csrf_exempt
def api_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True})

@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name', '')
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name
            )
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Auto login
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'email': user.email
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Override to filter by author if author parameter is provided"""
        queryset = Content.objects.all()
        author_id = self.request.query_params.get('author', None)
        
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get feed of content ordered by creation date"""
        contents = Content.objects.all().order_by('-created_at')
        page = self.paginate_queryset(contents)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(contents, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        content = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user,
            content=content
        )
        if created:
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already liked'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        content = self.get_object()
        Like.objects.filter(user=request.user, content=content).delete()
        return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        content = self.get_object()
        parent_id = request.data.get('parent_id')
        parent = None
        
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, content=content)
            except Comment.DoesNotExist:
                pass
        
        comment = Comment.objects.create(
            user=request.user,
            content=content,
            parent=parent,
            text=request.data.get('text', '')
        )
        
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return Response(
                {'error': 'You can only delete your own comments'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

# class RegisterView(APIView):
#     permission_classes = [permissions.AllowAny]
    
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             # Auto login after registration
#             login(request, user)
#             return Response({
#                 'user': UserSerializer(user).data,
#                 'message': 'Registration successful'
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create user profile explicitly
            from .models import UserProfile
            UserProfile.objects.get_or_create(user=user)
            
            # Auto login after registration
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            })
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})

class CosmicEventViewSet(viewsets.ModelViewSet):
    queryset = CosmicEvent.objects.all()
    serializer_class = CosmicEventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming cosmic events"""
        now = timezone.now()
        upcoming_events = CosmicEvent.objects.filter(
            event_date__gte=now
        ).order_by('event_date')[:10]
        
        serializer = self.get_serializer(upcoming_events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get events happening today"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        today_events = CosmicEvent.objects.filter(
            event_date__date__gte=today,
            event_date__date__lt=tomorrow
        )
        
        serializer = self.get_serializer(today_events, many=True)
        return Response(serializer.data)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Get user's content ONLY
        user_content = Content.objects.filter(author=user).order_by('-created_at')
        
        # Count likes and comments for user's posts
        total_likes = Like.objects.filter(content__author=user).count()
        total_comments = Comment.objects.filter(content__author=user).count()
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined
            },
            'profile': {
                'bio': profile.bio,
                'location': profile.location,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                'join_date': profile.join_date
            },
            'contents_count': user_content.count(),
            'total_likes': total_likes,
            'total_comments': total_comments
        })

        
class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]
    
    def put(self, request):
        user = request.user
        data = request.data.copy()
        
        # Update User model fields
        if 'email' in data:
            user.email = data['email']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        user.save()
        
        # Update UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        if 'bio' in data:
            profile.bio = data['bio']
        if 'location' in data:
            profile.location = data['location']
        profile.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(profile).data
        })

class AvatarUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if 'profile_picture' not in request.FILES:
            return Response({'error': 'No file provided'}, status=400)
        
        file = request.FILES['profile_picture']
        
        # Validate file size (max 2MB)
        if file.size > 2 * 1024 * 1024:
            return Response({'error': 'File too large. Max 2MB'}, status=400)
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            return Response({'error': 'Invalid file type. Use JPEG, PNG, GIF, or WebP'}, status=400)
        
        # Save the file
        profile.profile_picture = file
        profile.save()
        
        return Response({
            'message': 'Avatar updated successfully',
            'profile_picture': profile.profile_picture.url if profile.profile_picture else None
        })

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            return Response({'error': 'All fields are required'}, status=400)
        
        if new_password != confirm_password:
            return Response({'error': 'New passwords do not match'}, status=400)
        
        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters'}, status=400)
        
        # Check current password
        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, status=400)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Update session to prevent logout
        update_session_auth_hash(request, user)
        
        return Response({'message': 'Password changed successfully'})


# Mock AI Verification for astrophotos
def verify_astro_photo(category, location, timestamp):
    """Mock AI verification function"""
    from datetime import datetime
    import random
    
    # Simple verification logic
    verification_data = {
        'verified': random.choice([True, True, True, False]),  # 75% chance of verification
        'confidence': round(random.uniform(0.7, 0.95), 2),
        'reason': 'Analyzed against astronomical database'
    }
    
    # Adjust based on category
    if category in ['moon', 'planet']:
        verification_data['confidence'] = round(random.uniform(0.8, 0.98), 2)
        verification_data['reason'] = 'High confidence for planetary objects'
    elif category == 'eclipse':
        verification_data['confidence'] = round(random.uniform(0.9, 0.99), 2)
        verification_data['reason'] = 'Eclipse patterns matched'
    
    return verification_data

@login_required
def profile_view(request):
    """Render the user profile page"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get user's content
    user_content = Content.objects.filter(author=user).order_by('-created_at')
    
    context = {
        'user': user,
        'profile': profile,
        'contents': user_content,
        'contents_count': user_content.count(),
        'total_likes': Like.objects.filter(user=user).count(),
        'total_comments': Comment.objects.filter(user=user).count(),
    }
    
    return render(request, 'profile.html', context)  # Just 'profile.html'

def custom_logout(request):
    """Simple logout view that works with GET requests"""
    auth_logout(request)
    return redirect('/')
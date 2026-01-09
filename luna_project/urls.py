"""
URL configuration for luna_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from luna_app.views import custom_logout

ProfileView = login_required(TemplateView.as_view(template_name='luna_app/profile.html'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('luna_app.urls')),
    
    # Frontend routes
    path('', TemplateView.as_view(template_name='luna_app/index.html'), name='index'),
    path('community/', TemplateView.as_view(template_name='luna_app/community.html'), name='community'),
    path('auth/login/', TemplateView.as_view(template_name='luna_app/auth/login.html'), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('auth/signup/', TemplateView.as_view(template_name='luna_app/auth/signup.html'), name='signup'),
    path('app/write-article/', TemplateView.as_view(template_name='luna_app/app/write-article.html'), name='write-article'),
    path('app/upload-photo/', TemplateView.as_view(template_name='luna_app/app/upload-photo.html'), name='upload-photo'),
    path('app/edit-photo/', TemplateView.as_view(template_name='luna_app/app/edit-photo.html'), name='edit-photo'),
    path('app/edit-article/', TemplateView.as_view(template_name='luna_app/app/edit-article.html'), name='edit-article'),
    path('app/edit-content/', TemplateView.as_view(template_name='luna_app/app/edit-content.html'), name='edit-content'),
    path('profile/', ProfileView, name='profile'),
    path('auth/logout/', custom_logout, name='logout'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
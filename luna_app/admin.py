from django.contrib import admin
from .models import Content, Like, Comment, CosmicEvent, UserProfile

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'content_type', 'category', 'created_at']
    list_filter = ['content_type', 'category', 'ai_verified']
    search_fields = ['title', 'description', 'author__username']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'user__username']

@admin.register(CosmicEvent)
class CosmicEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'event_type']
    list_filter = ['event_type', 'event_date']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'join_date']

admin.site.register(Like)
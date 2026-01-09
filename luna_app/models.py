from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class CosmicEvent(models.Model):
    EVENT_TYPES = [
        ('meteor_shower', 'Meteor Shower'),
        ('planet', 'Planet'),
        ('eclipse', 'Eclipse'),
        ('conjunction', 'Conjunction'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['event_date']
    
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class Content(models.Model):
    CONTENT_TYPES = [
        ('photo', 'Photo'),
        ('article', 'Article'),
    ]
    
    CATEGORIES = [
        ('galaxy', 'Galaxy'),
        ('nebula', 'Nebula'),
        ('planet', 'Planet'),
        ('moon', 'Moon'),
        ('stars', 'Star Cluster'),
        ('eclipse', 'Eclipse'),
        ('astrophotography', 'Astrophotography Tips'),
        ('observation', 'Observation Logs'),
        ('science', 'Astronomy Science'),
        ('equipment', 'Equipment Reviews'),
        ('events', 'Celestial Events'),
        ('beginners', 'For Beginners'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contents')
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)  # For articles
    image = models.ImageField(upload_to='astrophotos/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)  # For external images
    location = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    ai_verified = models.BooleanField(default=False)
    ai_confidence = models.FloatField(default=0.0)
    ai_reason = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.content_type}: {self.title}"
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()

class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'content']
    
    def __str__(self):
        return f"{self.user.username} likes {self.content.title}"

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username}"
    
    @property
    def is_reply(self):
        return self.parent is not None
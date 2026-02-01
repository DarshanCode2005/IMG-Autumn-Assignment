from django.db import models
from django.conf import settings
from photos.models import Photo

class Engagement(models.Model):
    photo = models.OneToOneField(Photo, on_delete=models.CASCADE, related_name='engagement')
    likes_count = models.IntegerField(default=0)
    extra_metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Engagement for Photo {self.photo.id}"

class Like(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('photo', 'user')

class Comment(models.Model):
    engagement = models.ForeignKey(Engagement, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username}"

from django.db import models
from django.conf import settings
from events.models import Event

class Photo(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    original_image = models.ImageField(upload_to='photos/originals/')
    thumbnail_image = models.ImageField(upload_to='photos/thumbnails/', blank=True, null=True)
    watermarked_image = models.ImageField(upload_to='photos/watermarked/', blank=True, null=True)
    
    exif_data = models.JSONField(blank=True, null=True)
    ai_tags = models.JSONField(blank=True, null=True)
    manual_tags = models.JSONField(blank=True, null=True)
    
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_photos')
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.id} by {self.uploader.username}"

class TaggedIn(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='tagged_users')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tagged_in')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Tagged In"

from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True)
    date = models.DateField()
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    qr_code_path = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def __str__(self):
        return self.name

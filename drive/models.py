from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from io import BytesIO
from django.utils import timezone
from .pdf_utils import pdf_to_image
import os
from django.conf import settings

class Folder(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    is_trashed = models.BooleanField(default=False)
    parent_folder = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subfolders')
    shared_with = models.ManyToManyField(User, related_name='shared_folders', blank=True)
    last_used = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('folder_detail', args=[self.id])

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    is_trashed = models.BooleanField(default=False)
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.CASCADE, related_name='files')
    pdf_thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    shared_with = models.ManyToManyField(User, related_name='shared_files', blank=True)
    last_used = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('file_detail', args=[self.id])

    def get_thumbnail(self):
        # Check if the thumbnail is available
        if self.pdf_thumbnail:
            return self.pdf_thumbnail.url
        elif self.file.name.endswith(('jpg', 'jpeg', 'png')):
            return self.file.url
        elif self.file.name.endswith('pdf'):
            # Generate the thumbnail if it doesn't exist
            if not self.pdf_thumbnail:
                pdf_path = self.file.path
                thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', f'{self.pk}_thumbnail.png')
                pdf_to_image(pdf_path, thumbnail_path)
                self.pdf_thumbnail.save(f'{self.pk}_thumbnail.png', ContentFile(open(thumbnail_path, 'rb').read()))
                self.save()
            return 'thumbnails/' + f'{self.pk}_thumbnail.png'
        else:
            return 'static/default-thumbnail.png'
        
class Trash(models.Model):
    OBJECT_TYPE_CHOICES = [
        ('file', 'File'),
        ('folder', 'Folder'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Track which user owns the trash item
    object_id = models.PositiveIntegerField()  # ID of the original file or folder
    object_type = models.CharField(max_length=10, choices=OBJECT_TYPE_CHOICES)  # Type of the object
    name = models.CharField(max_length=255)  # Name of the file or folder
    deleted_at = models.DateTimeField(auto_now_add=True)  # When the item was deleted

    class Meta:
        verbose_name = "Trash Item"
        verbose_name_plural = "Trash Items"
    
    def __str__(self):
        return f"{self.name} ({self.object_type})"
        
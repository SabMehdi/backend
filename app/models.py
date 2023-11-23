from django.db import models
import hashlib

class FileAnalysis(models.Model):
    file_name = models.FilePathField(path='uploads/', recursive=True)
    file_hash = models.CharField(max_length=64, unique=True)  # Assuming SHA-256 hash
    inverted_index = models.JSONField()
    file_content = models.TextField()  # New field for storing file content
    file_path = models.CharField(max_length=1024)  # or models.TextField() if paths can be very long

    class Meta:
        app_label = 'app'
from django.db import models
import hashlib

class FileAnalysis(models.Model):
    file_path = models.FilePathField(path='uploads/', recursive=True)
    file_hash = models.CharField(max_length=64, unique=True)  # Assuming SHA-256 hash
    inverted_index = models.JSONField()
    file_content = models.TextField()  # New field for storing file content

    class Meta:
        app_label = 'app'
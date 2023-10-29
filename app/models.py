from django.db import models

class FileAnalysis(models.Model):
    file_path = models.FilePathField(path='uploads/', recursive=True)
    inverted_index = models.JSONField()
    class Meta:
        app_label = 'app'
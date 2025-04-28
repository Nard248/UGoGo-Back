from django.db import models

class ApplicationVersion(models.Model):
    version = models.CharField(max_length=50)
    release_date = models.DateField()

    def __str__(self):
        return f"Version {self.version} released on {self.release_date}"
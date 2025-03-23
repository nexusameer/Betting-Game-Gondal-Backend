from django.db import models

# Create your models here.

class Emails(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=255, unique=True)
    used=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.email
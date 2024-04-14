from django.db import models
from django.contrib.auth import get_user_model

from accounts.models import User
from communities.models import Community, Report


# Create your models here.

# File Management
class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.file.name
    
# notifications model
class Notification(models.Model):
    sender = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='sender')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='recipient')

    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    content = models.TextField()

    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



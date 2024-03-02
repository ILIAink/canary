from django.db import models

# Create your models here.

# report model
class Report(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    # the author user is optional (for anonymous reports)
    author = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)

    # users can attach media files to report (images, videos, etc)
    media = models.ManyToManyField('UploadedFile', blank=True)

    # users can specify how the report is handled from a few options
    # TODO this is super weird please make it better
    class ResolutionMethod(models.TextChoices):
        CANARY = 'CAN', 'Canary'
        EXTERNALLY = 'EXT', 'Externally'
        NO_CONTACT = 'NOC', 'No Contact'

    resolution_method = models.CharField(
        max_length=3,
        choices=ResolutionMethod.choices,
        default=ResolutionMethod.CANARY,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.file.name
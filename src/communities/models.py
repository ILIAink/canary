from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model
# Create your models here.


# main community model
class Community(models.Model):
    #class Meta:
        #app_label = 'communities'

    # each community has a unique id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    description = models.TextField()

    # each community stores a list of reports submitted to that community
    reports = models.ManyToManyField('Report')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# invite link model
class InviteLink(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    expiration_time = models.DateTimeField()
    # max uses for link, 0 means unlimited
    max_uses = models.IntegerField(default=0)
    used_count = models.IntegerField(default=0)

    def is_valid(self):
        return (self.used_count < self.max_uses or self.max_uses == 0) and self.expiration_time > timezone.now()

# community member relational model
class CommunityMember(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    member = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.member} in {self.community}'

# --- REPORT MODELS ----

# report model
class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    content = models.TextField()

    # the author user is optional (for anonymous reports)
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

    # users can specify how the report is handled from a few options
    class ResolutionMethod(models.TextChoices):
        CANARY = 'CAN', 'Canary'
        EXTERNALLY = 'EXT', 'Externally'
        NO_CONTACT = 'NOC', 'No Contact'

    resolution_method = models.CharField(
        max_length=3,
        choices=ResolutionMethod.choices,
        default=ResolutionMethod.CANARY,
    )

    # reports have a status, either "New", "In Progress", or "Resolved"
    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        IN_PROGRESS = 'INP', 'In Progress'
        RESOLVED = 'RES', 'Resolved'

    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.NEW,
    )

    # reports have a large text field for notes added by an admin
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # each file is associated with a report
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    def __str__(self):
        return self.file.name
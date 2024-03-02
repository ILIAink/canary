from django.db import models

# Create your models here.

# main community model
class Community(models.Model):
    name = models.CharField(max_length=100)

    description = models.TextField()

    # each community stores a list of foreign keys to reports submitted
    # each report is only stored in one community
    reports = models.ManyToManyField('reports.Report', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


# community member relational model
class CommunityMember(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    member = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.member} in {self.community}'
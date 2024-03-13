from django.contrib import admin

# Register your models here.
from .models import Community, Report
admin.site.register(Community)
admin.site.register(Report)
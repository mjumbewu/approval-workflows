from django.contrib import admin
from approval import models

admin.site.register(models.Workflow)
admin.site.register(models.State)
admin.site.register(models.Actor)
admin.site.register(models.Transition)
admin.site.register(models.Package)

from django.contrib import admin

from huscy.project_design import models


admin.site.register(models.Experiment)
admin.site.register(models.Session)
admin.site.register(models.DataAcquisitionMethod)
admin.site.register(models.DataAcquisitionMethodType)

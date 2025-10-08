from django.contrib import admin
from .models import *

# Register your dashboards models here.
admin.site.register(Dashboard)
admin.site.register(DashboardComponent)
admin.site.register(ComponentCriteria)
admin.site.register(DashboardFolder)

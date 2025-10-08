from django.contrib import admin
from horilla_crm.forecast.models import ForecastType,Forecast,ForecastTarget,ForecastTargetUser,ForecastCondition
# Register your forecasts models here.



admin.site.register(ForecastType)
admin.site.register(Forecast)
admin.site.register(ForecastTarget)
admin.site.register(ForecastTargetUser)
admin.site.register(ForecastCondition)
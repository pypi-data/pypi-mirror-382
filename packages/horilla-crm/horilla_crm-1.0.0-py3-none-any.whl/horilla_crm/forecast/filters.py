import django_filters

from horilla_crm.forecast.models import ForecastTarget, ForecastType
from horilla_generics.filters import HorillaFilterSet

# Define your forecasts filters here

class ForecastTargetFilter(HorillaFilterSet):
     class Meta:
        model = ForecastTarget
        fields='__all__'
        exclude = ['additional_info']
        search_fields = ['target_amount']



class ForecastTypeFilter(HorillaFilterSet):
     class Meta:
        model = ForecastType
        fields='__all__'
        exclude = ['additional_info']
        search_fields = ['name']


from django.forms import JSONField

from horilla_generics.filters import HorillaFilterSet

from .models import Dashboard  # Ensure your Report model is imported


class DashboardFilter(HorillaFilterSet):
    class Meta:
        model = Dashboard
        fields = '__all__'
        exclude = ['additional_info']
        search_fields = ['name']
       
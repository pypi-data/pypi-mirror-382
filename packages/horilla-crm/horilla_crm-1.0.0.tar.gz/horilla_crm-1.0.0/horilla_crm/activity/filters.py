import django_filters

from horilla_crm.activity.models import Activity
from horilla_generics.filters import HorillaFilterSet

# Define your activity filters here
class ActivityFilter(HorillaFilterSet):
     class Meta:
        model = Activity
        fields='__all__'
        exclude = ['additional_info','id']
        search_fields = ['subject', 'activity_type'] 
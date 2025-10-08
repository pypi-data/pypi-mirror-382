import django_filters
from horilla_generics.filters import HorillaFilterSet
from .models import Campaign

class CampaignFilter(HorillaFilterSet):
    class Meta:
        model = Campaign
        fields ='__all__'
        exclude = ['additional_info']
        search_fields = ['campaign_name']
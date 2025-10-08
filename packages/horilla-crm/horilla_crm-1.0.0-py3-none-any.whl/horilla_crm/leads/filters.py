from horilla_generics.filters import HorillaFilterSet
from horilla_crm.leads.models import Lead, LeadStatus

class LeadFilter(HorillaFilterSet):
     class Meta:
        model = Lead
        fields='__all__'
        exclude = ['additional_info']
        search_fields = ['first_name', 'email','title'] 


class LeadStatusFilter(HorillaFilterSet):
     class Meta:
        model = LeadStatus
        fields='__all__'
        exclude = ['additional_info']
        search_fields = ['name'] 
from horilla_generics.filters import HorillaFilterSet
from horilla_crm.opportunities.models import Opportunity, OpportunityStage ,BigDealAlert, OpportunityTeam,DefaultOpportunityMember

class OpportunityFilter(HorillaFilterSet):
     class Meta:
        model = Opportunity
        fields='__all__'
        exclude = ['additional_info']
        search_fields = ['name']


class OpportunityStageFilter(HorillaFilterSet):
     class Meta:
        model = OpportunityStage
        fields='__all__'
        exclude = ['additional_info']
        search_fields = ['name']

class OpportunityTeamFilter(HorillaFilterSet):
     class Meta:
        model = OpportunityTeam
        fields='__all__'
        exclude = ['additional_info']
        search_fields = ['team_name']

class OpportunityTeamMembersFilter(HorillaFilterSet):
     class Meta:
        model = DefaultOpportunityMember
        fields='__all__'
        exclude = ['additional_info']
        search_fields = ['user__first_name','user__last_name']






class BigDealAlertFilter(HorillaFilterSet):
    class Meta:
        model = BigDealAlert
        fields = '__all__'
        exclude = ['additional_info']
        search_fields = ['alert_name'] 

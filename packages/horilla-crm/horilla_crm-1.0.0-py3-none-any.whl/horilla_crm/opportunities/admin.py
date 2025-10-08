from django.contrib import admin

from horilla_crm.opportunities.models import Opportunity,OpportunityStage,OpportunityContactRole,OpportunityTeamMember,BigDealAlert,DefaultOpportunityMember,OpportunityTeam

# Register your opportunities models here.

admin.site.register(Opportunity)
admin.site.register(OpportunityStage)
admin.site.register(OpportunityContactRole)
admin.site.register(OpportunityTeamMember)
admin.site.register(BigDealAlert)
admin.site.register(DefaultOpportunityMember)
admin.site.register(OpportunityTeam)


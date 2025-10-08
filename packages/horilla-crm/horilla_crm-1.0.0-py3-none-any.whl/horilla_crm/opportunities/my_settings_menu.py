from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

from horilla.my_settings_registry import register

@register
class OpportunityTeamSettings:
    title = _("Opportunity Team")
    url = reverse_lazy("opportunities:opportunity_team_view")
    active_urls = ["opportunities:opportunity_team_view","opportunities:opportunity_team_detail_view"]
    hx_select_id = "#opportunity-team-view"
    order = 3

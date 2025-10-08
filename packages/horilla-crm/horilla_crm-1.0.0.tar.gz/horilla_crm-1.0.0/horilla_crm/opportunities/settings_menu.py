from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horilla.settings_sidebar import register
from horilla_crm.opportunities.models import BigDealAlert, OpportunityStage


@register
class OpportunitiesSettings:
    title = _("Opportunity")
    icon = "/assets/icons/oppor.svg"
    items = [
        {
            "label": OpportunityStage()._meta.verbose_name,
            "url": reverse_lazy("opportunities:opportunity_stage_view"),
            "hx-target": "#settings-content",
            "hx-push-url": "true",
            "hx-select": "#opportunity-stage-view",
            "hx-select-oob": "#settings-sidebar",
            "perm" : "opportunities.view_opportunitystage"
        },
        # {
        #     "label": BigDealAlert()._meta.verbose_name,
        #     "url": reverse_lazy("opportunities:big_deal_alert_view"),
        #     "hx-target": "#settings-content",
        #     "hx-push-url": "true",
        #     "hx-select": "#big-deal-alert-view",
        #     "hx-select-oob": "#settings-sidebar",
        #     "perm" : "opportunities.view_bigdealalert"
        # },
    ]

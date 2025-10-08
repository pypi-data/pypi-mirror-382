from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horilla.settings_sidebar import register
from horilla_crm.leads.models import LeadStatus


@register
class LeadsSettings:
    title = _("Lead")
    icon = "/assets/icons/lead1.svg"
    items = [
        {
            "label": LeadStatus()._meta.verbose_name,
            "url": reverse_lazy("leads:lead_stage_view"),
            "hx-target": "#settings-content",
            "hx-push-url": "true",
            "hx-select": "#leads-status-view",
            "hx-select-oob": "#settings-sidebar",
            "perm" : "leads.view_leadstatus"
        },
        
    ]

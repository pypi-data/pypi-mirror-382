from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horilla.floating_menu import register
from horilla_crm.leads.models import Lead


@register
class LeadFloating:
    title = Lead()._meta.verbose_name
    url = reverse_lazy("leads:leads_create")
    icon = "/assets/icons/leads.svg"
    items = {
        "hx-target": "#modalBox",
        "hx-swap": "innerHTML",
        "onclick": "openModal()",
        "perm" : ["leads.add_lead"]
    }

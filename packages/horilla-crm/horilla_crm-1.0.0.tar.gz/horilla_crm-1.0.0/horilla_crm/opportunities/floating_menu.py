from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horilla.floating_menu import register
from horilla_crm.opportunities.models import Opportunity


@register
class OpportunitiesFloating:
    title = Opportunity()._meta.verbose_name
    url = reverse_lazy("opportunities:opportunity_create")
    icon = "/assets/icons/opportunities.svg"
    items = {
        "hx-target": "#modalBox",
        "hx-swap": "innerHTML",
        "onclick": "openModal()",
        "perm" : ["opportunities.add_opportunity"]
    }

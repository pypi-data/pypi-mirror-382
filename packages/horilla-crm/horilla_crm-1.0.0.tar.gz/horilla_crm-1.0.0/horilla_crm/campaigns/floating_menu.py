from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horilla.floating_menu import register
from horilla_crm.campaigns.models import Campaign


@register
class CampaignFloating:
    title = Campaign()._meta.verbose_name
    url = reverse_lazy("campaigns:campaign_create")
    icon = "/assets/icons/campaign.svg"
    items = {
        "hx-target": "#modalBox",
        "hx-swap": "innerHTML",
        "onclick": "openModal()",
        "perm" : ["campaigns.add_campaign"]
    }

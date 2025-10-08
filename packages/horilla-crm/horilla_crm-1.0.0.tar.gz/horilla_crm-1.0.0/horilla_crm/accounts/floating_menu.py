from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horilla.floating_menu import register
from horilla_crm.accounts.models import Account


@register
class AccountFloating:
    title = Account()._meta.verbose_name
    url = reverse_lazy("accounts:account_create_form_view")
    icon = "/assets/icons/account.svg"
    items = {
        "hx-target": "#modalBox",
        "hx-swap": "innerHTML",
        "onclick": "openModal()",
        "perm" : ["accounts.add_account"]
    }

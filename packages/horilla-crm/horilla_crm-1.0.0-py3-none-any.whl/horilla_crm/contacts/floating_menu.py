from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horilla.floating_menu import register
from horilla_crm.contacts.models import Contact


@register
class ContactFloating:
    title = Contact()._meta.verbose_name
    url = reverse_lazy("contacts:contact_create_form")
    icon = "/assets/icons/contact.svg"
    items = {
        "hx-target": "#modalBox",
        "hx-swap": "innerHTML",
        "onclick": "openModal()",
        "perm" : ["contacts.add_contact"]
    }

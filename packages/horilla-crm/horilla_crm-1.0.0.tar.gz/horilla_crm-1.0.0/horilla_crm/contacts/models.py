from django.apps import apps
from django.db import models
from django.dispatch import receiver
from django.urls import reverse_lazy
from horilla_core.models import HorillaUser, HorillaCoreModel
from horilla_core.utils import compute_score
from horilla_utils.middlewares import _thread_local
from django.utils.translation import gettext_lazy as _
from horilla_core.models import LANGUAGE_CHOICES
from djmoney.settings import CURRENCY_CHOICES
from django.db.models.signals import pre_save



CONTACT_SOURCE_CHOICES = [
    ("web", "Web"),
    ("phone_inquiry", "Phone Inquiry"),
    ("partner_referral", "Partner Referral"),
    ("purchased_list", "Purchased List"),
    ("other", "Other"),
]


# Create your contacts models here.
class Contact(HorillaCoreModel):
    """Django model for Contact object."""

    contact_owner = models.ForeignKey(
        HorillaUser,
        on_delete=models.PROTECT,
        default="",
        verbose_name=_("Contact Owner"),
        related_name="owned_contacts",
    )
    title = models.CharField(
        verbose_name=_("Job Title"), max_length=100, blank=True, null=True
    )
    first_name = models.CharField(
        verbose_name=_("First Name"), max_length=80, blank=True, null=True
    )
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=80)
    email = models.EmailField(
        verbose_name=_("Email"), max_length=100, blank=True, null=True
    )
    phone = models.CharField(
        verbose_name=_("Phone"), max_length=40, blank=True, null=True
    )
    secondary_phone = models.CharField(
        verbose_name=_("Secondary Phone"), max_length=40, blank=True, null=True
    )
    
    address_city = models.CharField(
        verbose_name=_("City"), max_length=50, blank=True, null=True
    )
    address_state = models.CharField(
        verbose_name=_("State"), max_length=50, blank=True, null=True
    )
    address_zip = models.CharField(
        verbose_name=_("Zip"), max_length=20, blank=True, null=True
    )
    address_country = models.CharField(
        verbose_name=_("Country"), max_length=50, blank=True, null=True
    )
    parent_contact = models.ForeignKey(
        "self",
        verbose_name=_("Parent Contact"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_contacts",
    )
    contact_source = models.CharField(
        verbose_name=_("Contact Source"),
        max_length=50,
        choices=CONTACT_SOURCE_CHOICES,
        blank=True,
        null=True,
    )
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    birth_date = models.DateField(verbose_name=_("Birth Date"), blank=True, null=True)
    assistant = models.CharField(
        verbose_name=_("Assistant"), max_length=100, blank=True, null=True
    )
    assistant_phone = models.CharField(
        verbose_name=_("Assistant Phone"), max_length=40, blank=True, null=True
    )
    languages = models.CharField(
        verbose_name=_("Languages"),
        max_length=100,
        choices=LANGUAGE_CHOICES,
        blank=True,
        null=True
    )
    contact_currency = models.CharField(
        max_length=20,
        choices=CURRENCY_CHOICES,
        blank=True,
        null=True,
        help_text="Select your preferred currency",
        verbose_name=_("Contact Currency"),
    )
    is_primary = models.BooleanField(
        verbose_name=_("Is Primary"),
        default=False
    )
    contact_score = models.IntegerField(default=0, verbose_name=_("Contact Score"))

    OWNER_FIELDS = ["contact_owner"]


    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name}".strip()
    
    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('contacts:contact_update_form', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        """
        this method to get delete url for contact
        """
        return reverse_lazy('contacts:contact_delete', kwargs={'pk': self.pk})
    
    def get_child_contact_delete_url(self):
        """
        this method to get delete url for child contact
        """
        return reverse_lazy('contacts:delete_child_contacts', kwargs={'pk': self.pk})
    
    def get_change_owner_url(self):
        """
        This method to get change owner url
        """

        return reverse_lazy('contacts:contact_change_owner',kwargs={'pk': self.pk})
    
    def get_detail_url(self):
        """
        This method to get detail view url
        """

        return reverse_lazy('contacts:contact_detail_view', kwargs={'pk':self.pk})
    
    def get_opportunity_contact_role_edit_url(self, opportunity=None):
        try:
            request = getattr(_thread_local, 'request', None)
            if request and hasattr(request, 'resolver_match'):
                object_id = request.resolver_match.kwargs.get('pk')
                if object_id:
                    model = apps.get_model('opportunities', 'Opportunity')
                    opportunity = model.objects.get(pk=object_id)
            if opportunity:
                ocr = self.opportunity_roles.get(opportunity=opportunity)

            return ocr.get_edit_url() if ocr else None
        except :
            return None
    
@receiver(pre_save, sender=Contact)
def update_contact_score(sender, instance, **kwargs):
    instance.contact_score = compute_score(instance)
    

class ContactAccountRelationship(HorillaCoreModel):
    
    contact = models.ForeignKey(
        "contacts.Contact",
        on_delete=models.CASCADE,
        related_name="account_relationships",
        verbose_name=_("Contact")
    )
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="contact_relationships",
        verbose_name=_("Account")
    )
    role = models.ForeignKey(
        "horilla_core.CustomerRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Role")
    )

    class Meta:
        unique_together = ("contact", "account")
        verbose_name = _("Contact Account Relationship")
        verbose_name_plural = _("Contact Account Relationships")

    def __str__(self):
        return f"{self.contact} - {self.account} ({self.role})"
    
    

    def get_edit_account_contact_relation_url(self):
        """
        This method is to gte the update url for contact account relation
        """

        return reverse_lazy('accounts:edit_account_contact_relation',kwargs={'pk':self.pk})
    
    def get_edit_url_contact_account(self):
        """
        This method is to gte the update url for contact account relation
        """

        return reverse_lazy('contacts:edit_contact_account_relation',kwargs={'pk':self.pk})
    
    def get_delete_url(self):
        """
        this methos is to get related account delete url
        """
        return reverse_lazy('contacts:delete_related_accounts', kwargs={'pk':self.pk})
    


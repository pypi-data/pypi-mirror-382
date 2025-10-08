from django.apps import apps
from django.db import models
from django.forms import ValidationError
from django.urls import reverse_lazy
from django.conf import settings
from auditlog.models import AuditlogHistoryField
from django.utils.translation import gettext_lazy as _
from horilla_core.models import HorillaUser, HorillaCoreModel, MultipleCurrency
from horilla_crm.leads.models import Lead
from horilla_utils.middlewares import _thread_local


# class Contact(HorillaCoreModel):
#     """
#     Simple Contact model with title and contact name.
#     """
#     title = models.CharField(max_length=100, verbose_name=_("Title"))
#     contact_name = models.CharField(max_length=255, verbose_name=_("Contact Name"))

#     def __str__(self):
#         return f"{self.contact_name}"

#     class Meta:
#         verbose_name = _("Contact")
#         verbose_name_plural = _("Contacts")

class CampaignMember(HorillaCoreModel):
    """
    Model representing a member (Lead or Contact) associated with a campaign.
    """

    CAMPAIGN_MEMBER_STATUS = [
        ('planned', 'Planned'),
        ('sent', 'Sent'),
        ('recieved','Recieved'),
        ('responded','Responded')

    ]
    MEMBER_TYPE_CHOICES = [
        ('lead', 'Lead'),
        ('contact', 'Contact'),
    ]
    campaign = models.ForeignKey(
        'Campaign',
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name=_("Campaign")
    )
    lead = models.ForeignKey(
         "leads.Lead",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaign_members",
        verbose_name=_("Lead")
    )
    member_status = models.CharField(
        max_length=20,
        choices=CAMPAIGN_MEMBER_STATUS,
        verbose_name=_("Member Status")
    )
    contact = models.ForeignKey(
         "contacts.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaign_members",
        verbose_name=_("Contact")
    )
    member_type = models.CharField(
        max_length=10,
        choices=MEMBER_TYPE_CHOICES,
        verbose_name=_("Type"),default='lead'
    )

    def get_detail_view(self, object_model=None, object_id=None):
        """
        Returns the detail view URL for the associated Lead or Contact based on member_type.
        Falls back to request query parameters or self.member_type if object_model or object_id is not provided.
        """
        try:
            if self.member_type == 'lead':
                model_instance = self.lead
                if model_instance and hasattr(model_instance, 'get_detail_url'):
                    return model_instance.get_detail_url()
            elif self.member_type == 'contact':
                model_instance = self.contact
                if model_instance and hasattr(model_instance, 'get_detail_url'):
                    return model_instance.get_detail_url()
            
            return "#"
        except Exception as e:
            return "#"
        

    def get_detail_view_of_contact_campaign(self):
        """
        Method to get the detail view url of the campaign for contact related campaigns
        """

        model_instance  = self.campaign
        if model_instance and hasattr(model_instance, 'get_detail_view_url'):
            return model_instance.get_detail_view_url()
        
            
    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('campaigns:edit_campaign_member', kwargs={'pk': self.pk})

    def get_edit_campaign_member(self):
        """
        This method to get edit url
        """
        return reverse_lazy('campaigns:edit_added_campaign_members', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        """
        This method to get delete url
        """
        return reverse_lazy('campaigns:delete_campaign_member', kwargs={'pk': self.pk})
    
    def get_edit_contact_to_campaign_url(self):
        """
        This method to get the edit url for add contact to camapign
        """

        return reverse_lazy('campaigns:edit_contact_to_campaign',kwargs={'pk':self.pk})
    
    def get_delete_contact_to_campaign_url(self):
        """
        This method is to get delete url for added contact to campaign
        """

        return reverse_lazy('campaigns:delete_campaign_contact_member',kwargs={'pk':self.pk})

    def get_title(self):
        """
        Return the appropriate title based on member_type.
        """
        if self.member_type == 'lead' and self.lead:
            return self.lead.title
        elif self.member_type == 'contact' and self.contact:
            return str(self.contact)
        return None
    

    def __str__(self):
        if self.member_type == 'lead' and self.lead:
            return f"{self.lead} in {self.campaign}"
        elif self.member_type == 'contact' and self.contact:
            return f"{self.contact} in {self.campaign}"
        return f"Unknown member in {self.campaign}"
    
    class Meta:
        verbose_name = _("Campaign Member")
        verbose_name_plural = _("Campaign Members")
    
    def clean(self):
        """
        Custom validation to check for duplicates
        """
        super().clean()
        
        # Check for duplicate lead in same campaign
        if self.member_type == 'lead' and self.lead and self.campaign:
            existing = CampaignMember.objects.filter(
                campaign=self.campaign,
                lead=self.lead
            ).exclude(pk=self.pk if self.pk else None)
            
            if existing.exists():
                raise ValidationError("This lead already has this campaign.")
        
        # Check for duplicate contact in same campaign
        elif self.member_type == 'contact' and self.contact and self.campaign:
            existing = CampaignMember.objects.filter(
                campaign=self.campaign,
                contact=self.contact
            ).exclude(pk=self.pk if self.pk else None)
            
            if existing.exists():
                raise ValidationError("This contact already has this campaign.")
            

    @property
    def campaign_type_display(self):
        if self.campaign:
            return self.campaign.get_campaign_type_display()
        return ""


   

class Campaign(HorillaCoreModel):
    """
    Model representing a marketing campaign.
    """
    CAMPAIGN_STATUS_CHOICES = [
        ('new', 'New'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('aborted', 'Aborted'),

    ]
    
    CAMPAIGN_TYPE_CHOICES = [
        ('email', 'Email'),
        ('event', 'Event'),
        ('social_media', 'Social Media'),
        ('other', 'Other'),
    ]
    
    campaign_name = models.CharField(max_length=255, verbose_name=_("Campaign Name"))
    campaign_owner = models.ForeignKey(HorillaUser, on_delete=models.PROTECT, default="",verbose_name=_("Campaign Owner"),related_name="campaign")
    status = models.CharField(
        max_length=20,
        choices=CAMPAIGN_STATUS_CHOICES,
        default='planned',
        verbose_name=_("Status")
    )
    campaign_type = models.CharField(
        max_length=20,
        choices=CAMPAIGN_TYPE_CHOICES,
        verbose_name=_("Type")
    )
    start_date = models.DateField(blank=True,null=True,verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
    campaign_currency = models.ForeignKey(
        MultipleCurrency, on_delete=models.PROTECT, default="", null=True, blank=True, verbose_name=_("Campaign Currency")
    )
    expected_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Expected Revenue")
    )
    budget_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Budget Cost")
    )
    actual_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Actual Cost")
    )
    expected_response = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Expected Response (%)")
    )
    number_sent = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Number Sent in Campaign")
    )
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    parent_campaign = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_campaigns",
        verbose_name=_("Parent Campaign")
    )


    OWNER_FIELDS = ["campaign_owner"]
    
    

    def __str__(self):
        return f'{self.campaign_name}-{self.pk}'

    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

       

    def get_edit_campaign_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('campaigns:campaign_edit', kwargs={'pk': self.pk})
    

    def get_change_owner_url(self):
        """
        This method to get change owner url
        """
        return reverse_lazy('campaigns:campaign_change_owner', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        """
        This method to get delete url
        """
        return reverse_lazy('campaigns:campaign_delete', kwargs={'pk': self.pk})
    
    def get_delete_child_campaign_url(self):
        """
        This method to get  delete child campaign url
        """
        return reverse_lazy('campaigns:delete_child_campaign', kwargs={'pk': self.pk})
    
    def get_detail_view_url(self):
        """
        This method to get detail view url
        """

        return reverse_lazy('campaigns:campaign_detail_view', kwargs={'pk':self.pk})
    
    def get_specific_member_edit_url(self, object_model=None, object_id=None):
        """
        Returns the edit URL for the CampaignMember linked to the given object_model and object_id.
        Falls back to request query parameters if not provided.
        """
        try:    
            request = getattr(_thread_local, 'request', None)
            if request:
                object_model = request.GET.get('model_name', '').lower()
                object_id = request.resolver_match.kwargs.get('pk')
            field_name = 'lead'
            filter_kwargs = {
                'campaign': self,
                field_name: apps.get_model('leads', object_model.capitalize()).objects.get(pk=object_id)
            }
            member = self.members.filter(**filter_kwargs).first()
            return member.get_edit_url()
        except Exception as e:
            return "#"
        
        
    def get_edit_contact_to_campaign_url_for_contact(self, contact=None):
        """
        Return the edit URL for the CampaignMember linking this campaign and a given contact.
        If contact is None, tries to retrieve from request context (pk).
        """

        try:
            request = getattr(_thread_local, 'request', None)
            if request and hasattr(request, 'resolver_match'):
                object_id = request.resolver_match.kwargs.get('pk')
                if object_id:
                    model = apps.get_model('contacts', 'Contact')
                    contact = model.objects.get(pk=object_id)
            if contact:
                ocr = self.members.get(contact=contact)

            return ocr.get_edit_contact_to_campaign_url() if ocr else None
        except :
            return None
        

    def get_delete_contact_to_campaign_url_for_contact(self):
        """
        this methos is to get related account delete url
        """
        try:
            request = getattr(_thread_local, 'request', None)
            if request and hasattr(request, 'resolver_match'):
                object_id = request.resolver_match.kwargs.get('pk')
                if object_id:
                    model = apps.get_model('contacts', 'Contact')
                    contact = model.objects.get(pk=object_id)
            if contact:
                ocr = self.members.get(contact=contact)

            return ocr.get_delete_contact_to_campaign_url() if ocr else None
        except :
            return None

        
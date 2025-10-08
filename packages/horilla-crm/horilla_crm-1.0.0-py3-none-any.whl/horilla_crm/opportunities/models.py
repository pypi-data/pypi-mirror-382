from django.db import models
from django.urls import reverse_lazy
from horilla_core.utils import compute_score
from horilla_crm.accounts.models import Account
from horilla_crm.campaigns.models import Campaign
from horilla_crm.contacts.models import Contact
from horilla_utils.methods import render_template
from horilla_core.models import Company, HorillaUser, CustomerRole, HorillaCoreModel, MultipleCurrency
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.db.models.signals import pre_save


class OpportunityStage(HorillaCoreModel):
    
    """Opportunity Stage model for flexible stage management"""

    STAGE_TYPE_CHOICES = [
        ('open', _('Open')),
        ('won', _('Closed Won')),
        ('lost', _('Closed Lost')),
    ]

    name = models.CharField(max_length=100, verbose_name=_("Stage Name"))
    order = models.PositiveIntegerField(
        verbose_name=_("Order"), help_text="Order in which stages appear"
    )
    probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Probability"),
        help_text="Default probability percentage for this stage",
    )
    is_final = models.BooleanField(default=False, verbose_name=_("Is Final Stage"))
    stage_type = models.CharField(
        max_length=10,
        choices=STAGE_TYPE_CHOICES,
        default='open',
        verbose_name=_("Stage Type"),
        help_text=_("Type of stage - Open, Closed Won, or Closed Lost")
    )



    def is_final_col(self):
        """ Returns the HTML for the is_final column in the list view. """
        html =  render_template(
            path="opportunity_stage/is_final_col.html",
            context={"instance": self},  
        )
        return mark_safe(html)
    
    def clean(self):
        if self.order < 0:
            raise ValidationError(_("Order must be a non-negative integer."))
    
    @property
    def is_won(self):
        """Helper property to check if this is a won stage"""
        return self.stage_type == 'won'
    
    @property
    def is_lost(self):
        """Helper property to check if this is a lost stage"""
        return self.stage_type == 'lost'
    
    @property
    def is_closed(self):
        """Helper property to check if this is any closed stage"""
        return self.stage_type in ['won', 'lost']
        
    def save(self, *args, **kwargs):
        with transaction.atomic():
            previous_final = None
            if self.is_final:
                # Identify and unset the current final stage for the company
                previous_final = OpportunityStage.objects.filter(
                    is_final=True, company=self.company
                ).exclude(pk=self.pk).first()
                if previous_final:
                    OpportunityStage.objects.filter(pk=previous_final.pk).update(is_final=False)

            if self.pk is None:
                # For new stages, use provided order or next available order
                if not self.order:
                    self.order = self.get_next_order_for_company(self.company)
                self._desired_position = self.order if not self.is_final else None
            else:
                original = OpportunityStage.objects.get(pk=self.pk)
                is_final_changed = self.is_final != original.is_final

                # Use provided order for updates, unless it's a new final stage
                if is_final_changed or self.order != original.order:
                    self._desired_position = self.order if not self.is_final else None

            super().save(*args, **kwargs)
            self._reorder_all_statuses(previous_final=previous_final)

    def _reorder_all_statuses(self, previous_final=None):
        """
        Reorder all statuses for the company to ensure sequential ordering with final stage last.
        If desired_position is specified (non-final stage), insert at that position and shift others.
        If desired_position is higher than max order or stage is final, place just before final stage.
        Previous final stage is placed just before the new final stage.
        Only affects statuses within the same company.
        """
        company_statuses = list(
            OpportunityStage.objects.filter(company=self.company).order_by('order', 'pk')
        )
        
        final_statuses = [s for s in company_statuses if s.is_final]
        non_final_statuses = [s for s in company_statuses if not s.is_final]
        
        if len(final_statuses) > 1:
            if self.is_final and self in final_statuses:
                final_statuses = [self]
            else:
                final_statuses = final_statuses[:1]
            for status in [s for s in company_statuses if s.is_final and s not in final_statuses]:
                OpportunityStage.objects.filter(pk=status.pk).update(is_final=False)
        
        if hasattr(self, '_desired_position') and self._desired_position is not None:
            desired_order = self._desired_position
            non_final_statuses = [s for s in non_final_statuses if s != self]
            non_final_statuses.sort(key=lambda x: x.order)

            max_order = max([s.order for s in non_final_statuses], default=0)

            if desired_order > max_order:
                non_final_statuses.append(self)
            else:
                non_final_statuses.insert(max(0, desired_order - 1), self)
        else:
            non_final_statuses.sort(key=lambda x: x.order)

        if previous_final and previous_final in non_final_statuses:
            non_final_statuses.remove(previous_final)
            reordered_statuses = non_final_statuses + [previous_final] + final_statuses
        else:
            reordered_statuses = non_final_statuses + final_statuses
        
        with transaction.atomic():
            for i, status in enumerate(reordered_statuses, 1):
                OpportunityStage.objects.filter(pk=status.pk).update(order=i)
        
        if hasattr(self, '_desired_position'):
            delattr(self, '_desired_position')
    

    @receiver(post_delete, sender='opportunities.OpportunityStage')
    def handle_bulk_delete(sender, instance, **kwargs):
        """
        Handle bulk deletions or queryset deletions by reordering remaining statuses
        and setting the last stage as final if no final stage exists.
        """
        with transaction.atomic():
            try:
                company = instance.company  # Attempt to access the company
                # Ensure the company exists in the database
                if not Company.objects.filter(pk=company.pk).exists():
                    return  
                was_final = instance.is_final
                remaining_statuses = list(
                    OpportunityStage.objects.filter(company=company).order_by('order')
                )
                for i, status in enumerate(remaining_statuses, 1):
                    OpportunityStage.objects.filter(pk=status.pk).update(order=i)
                if was_final and remaining_statuses and not any(s.is_final for s in remaining_statuses):
                    last_stage = remaining_statuses[-1]
                    OpportunityStage.objects.filter(pk=last_stage.pk).update(is_final=True)
            except Company.DoesNotExist:
                return  


    @classmethod
    def get_next_order_for_company(cls, company):
        """
        Get the next available order number for a company, just before final stage
        """
        max_order = cls.objects.filter(company=company, is_final=False).aggregate(
            max_order=models.Max('order')
        )['max_order']
        return (max_order or 0) + 1
    
    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('opportunities:edit_opportunity_stage', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        """
        This method to get delete url
        """
        return reverse_lazy('opportunities:delete_opportunity_stage', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _("Opportunity Stage")
        verbose_name_plural = _("Opportunity Stages")
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'company'],
                name='unique_stage_name_per_company'
            ),
            models.UniqueConstraint(
                fields=['order', 'company'],
                name='unique_stage_order_per_company'
            ),
        ]


    def __str__(self):
        return self.name


class Opportunity(HorillaCoreModel):
    """Django model based on Salesforce Opportunity object"""

    TYPE_CHOICES = [
        ("existing_customer_upgrade", "Existing Customer - Upgrade"),
        ("existing_customer_replacement", "Existing Customer - Replacement"),
        ("existing_customer_downgrade", "Existing Customer - Downgrade"),
        ("new_customer", "New Customer"),
    ]

    LEAD_SOURCES = [
        ("website", _("Website")),
        ("referral", _("Referral")),
        ("event", _("Event")),
        ("campaign", _("Campaign")),
        ("phone", _("Phone")),
        ("email", _("Email")),
        ("social media", _("Social Media")),
        ("partner", _("Partner")),
        ("other", _("Other")),
    ]

    FORECAST_CATEGORY_CHOICES = [
        ("omitted", "Omitted"),
        ("pipeline", "Pipeline"),
        ("best_case", "Best Case"),
        ("commit", "Commit"),
        ("closed", "Closed"),
    ]

    DELIVERY_STATUS_CHOICES = [
        ("yet_to_fulfill", "Yet to Fulfill"),
        ("partially_delivered", "Partially Delivered"),
        ("completely_delivered", "Completely Delivered"),
    ]

    name = models.CharField(
        max_length=120, verbose_name=_("Opportunity Name"), help_text="Opportunity Name"
    )
    amount = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, verbose_name=_("Amount")
    )
    expected_revenue = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Expected Revenue"),
    )
    quantity = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Quantity"),
        help_text="Total Opportunity Quantity",
    )
    close_date = models.DateField(null=True, blank=True, verbose_name=_("Close Date"))
    stage = models.ForeignKey(
        OpportunityStage,
        on_delete=models.PROTECT,
        verbose_name=_("Stage"),
        help_text="Current opportunity stage",
    )
    probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Probability"),
        help_text="Probability percentage (0-100)",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    description = models.TextField(
        max_length=32000, blank=True, verbose_name=_("Description")
    )
    next_step = models.CharField(
        max_length=255, blank=True, verbose_name=_("Next Step")
    )
    opportunity_score = models.IntegerField(default=0, verbose_name=_("Opportunity Score"))
    primary_campaign_source = models.ForeignKey(
        Campaign,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Primary Campaign Source"),
        related_name="opportunities",
    )
    owner = models.ForeignKey(
        HorillaUser,
        on_delete=models.PROTECT,
        verbose_name=_("Owner"),
        help_text="Opportunity Owner",
    )
    opportunity_type = models.CharField(
        max_length=50, choices=TYPE_CHOICES, blank=True, verbose_name=_("Type")
    )
    lead_source = models.CharField(
        max_length=50, choices=LEAD_SOURCES, blank=True, verbose_name=_("Lead Source")
    )
    forecast_category = models.CharField(
        max_length=50,
        choices=FORECAST_CATEGORY_CHOICES,
        blank=True,
        verbose_name=_("Forecast Category"),
    )
    delivery_installation_status = models.CharField(
        max_length=50,
        choices=DELIVERY_STATUS_CHOICES,
        blank=True,
        verbose_name=_("Delivery Installation Status"),
    )
    main_competitors = models.CharField(
        max_length=100, blank=True, verbose_name=_("Main Competitors")
    )
    order_number = models.CharField(
        max_length=8, blank=True, verbose_name=_("Order Number")
    )
    tracking_number = models.CharField(
        max_length=12, blank=True, verbose_name=_("Tracking Number")
    )
    opportunity_currency = models.ForeignKey(
        MultipleCurrency,
        on_delete=models.PROTECT,
        default="",
        null=True,
        blank=True,
        verbose_name=_("Opportunity Currency"),
        related_name="opportunity_currency"
    )
    account  = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        default="",
        null=True,
        blank=True,
        verbose_name=_("Account"),
        related_name="opportunity_account"
    )

    OWNER_FIELDS = ["owner"]

    class Meta:
        verbose_name = _("Opportunity")
        verbose_name_plural = _("Opportunities")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}"

    DYNAMIC_METHODS = ["get_change_owner_url", "get_edit_url", "get_detail_url"]

    def get_change_owner_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy(
            "opportunities:opportunity_change_owner", kwargs={"pk": self.pk}
        )

    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy("opportunities:opportunity_edit", kwargs={"pk": self.pk})
    
    def get_delete_url(self):
        """
        This method to get delete url
        """
        return reverse_lazy("opportunities:opportunity_delete", kwargs={"pk": self.pk})

    def get_detail_url(self):
        """
        This method to get delete url
        """
        return reverse_lazy(
            "opportunities:opportunity_detail_view", kwargs={"pk": self.pk}
        )

    def set_forecast_category(self):
        """
        Set forecast_category based on the stage's probability and status.
        """
        if not self.stage:
            self.forecast_category = "omitted"
            return

        # If stage is lost, set to omitted
        if self.stage.is_lost:
            self.forecast_category = "omitted"

        # If stage is won, set to closed
        elif self.stage.is_won:
            self.forecast_category = "closed"
            
        # Otherwise, map probability to forecast category
        else:
            probability = self.probability or self.stage.probability or 0
            if probability < 10:
                self.forecast_category = "omitted"
            elif 10 <= probability <= 40:

                self.forecast_category = "pipeline"
            elif 41 <= probability <= 70:
                self.forecast_category = "best_case"
            elif 71 <= probability <= 99:
                self.forecast_category = "commit"
            elif probability == 100:
                self.forecast_category = "closed"

    def save(self, *args, **kwargs):
        if self.stage:
            self.probability = self.stage.probability
        if self.amount is not None and self.probability is not None:
            self.expected_revenue = self.amount * (self.probability / 100)
        self.set_forecast_category()
        
        super().save(*args, **kwargs)


@receiver(pre_save, sender=Opportunity)
def update_opportunity_score(sender, instance, **kwargs):
    instance.opportunity_score = compute_score(instance)

class OpportunityContactRole(HorillaCoreModel):
    
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='opportunity_roles',
        verbose_name='Contact',
        null=False,
        blank=False
    )
    
    opportunity = models.ForeignKey(
        Opportunity, 
        on_delete=models.CASCADE,
        related_name='contact_roles',
        verbose_name='Opportunity',
        null=False,
        blank=False
    )
    
    is_primary = models.BooleanField(
        default=False,
        verbose_name='Primary'
    )
    
    role = models.ForeignKey(
        CustomerRole,
        on_delete=models.SET_NULL,
        related_name='opportunity_contact_roles',
        verbose_name=_("Role"),
        null=True,
        blank=True
    )


    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('opportunities:edit_opportunity_contact_role', kwargs={'pk': self.pk})
    
    
  
    
    class Meta:
        verbose_name = 'Opportunity Contact Role'
        verbose_name_plural = 'Opportunity Contact Roles'
        unique_together = ('contact', 'opportunity') 

    def __str__(self):
        return f"{self.contact} - {self.opportunity} ({self.role})"


TEAM_ROLE_CHOICES = [
        ('account_manager', _('Account Manager')),
        ('channel_manager', _('Channel Manager')),
        ('executive_sponsor', _('Executive Sponsor')),
        ('lead_qualifier', _('Lead Qualifier')),
        ('pre_sales_consultant', _('Pre-Sales Consultant')),
        ('sales_manager', _('Sales Manager')),
        ('sales_rep', _('Sales Rep')),
        ('opportunity_owner', _('Opportunity Owner')),
    ]

ACCESS_LEVEL_CHOICES = [
        ('read', _('Read Only')),
        ('edit', _('Read/Write')),
        ('owner', _('Owner')),
    ]

class OpportunityTeam(HorillaCoreModel):

    team_name = models.CharField(max_length=255, verbose_name=_("Team Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    owner = models.ForeignKey(
        HorillaUser,
        on_delete=models.PROTECT,
        related_name='owner',
        verbose_name=_('Owner')
    )


    class Meta:
        verbose_name = _('Opportunity Team')
        verbose_name_plural = _('Opportunity Teams')

    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('opportunities:edit_opportunity_team', kwargs={'pk': self.pk})
    
    def get_detail_view_url(self):
        """
        This method to get detail view url
        """
        return reverse_lazy('opportunities:opportunity_team_detail_view', kwargs={'pk':self.pk})
    
    def get_delete_url(self):
        """
        This method to get delete url
        """
        return reverse_lazy('opportunities:delete_opportunity_team', kwargs={'pk':self.pk})
    

    

    

class OpportunityTeamMember(HorillaCoreModel):

   
    opportunity = models.ForeignKey(
        'Opportunity',
        on_delete=models.CASCADE,
        related_name='opportunity_team_members',
        verbose_name=_('Opportunity')
    )
    opportunity_access = models.CharField(
        max_length=255,
        choices=ACCESS_LEVEL_CHOICES,
        default='Read',
        verbose_name=_('Opportunity Access')
    )
    team_role = models.CharField(
        max_length=255,
        choices=TEAM_ROLE_CHOICES,
        verbose_name=_('Member Role')
    )
    user = models.ForeignKey(
        HorillaUser,
        on_delete=models.PROTECT,
        related_name='opportunty_team_users',
        verbose_name=_('Team Members')
    )

    class Meta:
        verbose_name = _('Opportunity team member')
        verbose_name_plural = _('Opportunity team members')

    def __str__(self):
        return f"{self.user} - {self.team_role}"
    

class DefaultOpportunityMember(HorillaCoreModel):
    """
    Default team members that get automatically added to new opportunities
    """
    team = models.ForeignKey(
        'OpportunityTeam',
        on_delete=models.CASCADE,
        related_name='team_members',
        verbose_name=_('Team Name')
    )

    user = models.ForeignKey(
        HorillaUser,
        on_delete=models.CASCADE,
        related_name='default_opportunity_memberships',
        verbose_name=_('Team Member')
    )
    
    team_role = models.CharField(
        max_length=255,
        choices=TEAM_ROLE_CHOICES,
        verbose_name=_('Member Role')
    )
    
    opportunity_access_level = models.CharField(
        choices=ACCESS_LEVEL_CHOICES,
        max_length=20,
        verbose_name=_('Access Level')
    )
    
    class Meta:
        verbose_name = _('Default Opportunity Member')
        verbose_name_plural = _('Default Opportunity Members')
        unique_together = ('user','team')

    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('opportunities:edit_opportunity_team_member', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        """
        This method to get delete url
        """
        return reverse_lazy('opportunities:delete_opportunity_team_member', kwargs={'pk':self.pk})
    
    

    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class BigDealAlert(HorillaCoreModel):
    """Model to store Big Deal Alert configuration."""
    
    alert_name = models.CharField(max_length=255, verbose_name=_("Alert Name"))
    
    trigger_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00, verbose_name=_("Trigger Amount")
    )
    
    trigger_probability = models.PositiveIntegerField(
        default=0, verbose_name=_("Trigger Probability"),
        help_text=_("Trigger alert when opportunity probability reaches this percentage")
    )
    
    sender_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Sender Name"))
    sender_email = models.EmailField(blank=True, null=True, verbose_name=_("Sender Email"))
    
    notify_emails = models.TextField(
        blank=True, null=True, verbose_name=_("Notify Emails"),
        help_text=_("Comma-separated emails to notify")
    )
    notify_cc_emails = models.TextField(blank=True, null=True, verbose_name=_("Notify CC Emails"))
    notify_bcc_emails = models.TextField(blank=True, null=True, verbose_name=_("Notify BCC Emails"))
    
    notify_opportunity_owner = models.BooleanField(default=False, verbose_name=_("Notify Opportunity Owner"))
    active = models.BooleanField(default=False, verbose_name=_("Active"))  # Add active field
    
    
    class Meta:
        verbose_name = _("Big Deal Alert")
        verbose_name_plural = _("Big Deal Alerts")
    
    def __str__(self):
        return self.alert_name
    
    def notify_email_list(self):
        return [email.strip() for email in self.notify_emails.split(",")]
    
    def notify_cc_emails_list(self):
        return [email.strip() for email in self.notify_cc_emails.split(",")]

    def notify_bcc_emails_list(self):
        return [email.strip() for email in self.notify_bcc_emails.split(",")]
    
    def active_return(self):
        return "Yes" if self.notify_opportunity_owner else "No"
    
    def probality_return(self):
        return f"{self.trigger_probability} %"
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy



from horilla_core.models import HorillaCoreModel, HorillaUser, Period, Quarter, FiscalYearInstance, Role
from horilla_crm.opportunities.models import Opportunity  


class ForecastType(HorillaCoreModel):
    """
    Defines different types of forecasts (e.g., Revenue, Quantity, etc.)
    """
    FORECAST_TYPE_CHOICES = [
        ('deal_revenue_amount', _('Deal Revenue Amount')),
        ('deal_revenue_expected_amount', _('Deal Revenue Expected Amount')),
        ('deal_quantity', _('Deal Quantity')),
    ]
    name = models.CharField(max_length=100, verbose_name=_("Forecast Type Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    forecast_type = models.CharField(
        max_length=50,
        choices=FORECAST_TYPE_CHOICES,
        default='deal_revenue_amount',
        verbose_name=_("Forecast Type")
    )
    
    include_pipeline = models.BooleanField(default=True, verbose_name=_("Include Pipeline"))
    include_best_case = models.BooleanField(default=True, verbose_name=_("Include Best Case"))
    include_commit = models.BooleanField(default=True, verbose_name=_("Include Commit"))
    include_closed = models.BooleanField(default=True, verbose_name=_("Include Closed"))
   
    
    class Meta:
        verbose_name = _("Forecast Type")
        verbose_name_plural = _("Forecast Types")
        
    def __str__(self):
        return self.name
    
    @property
    def is_revenue_based(self):
        """Check if this forecast type is revenue-based (either amount or expected amount)"""
        return self.forecast_type in ['deal_revenue_amount', 'deal_revenue_expected_amount']
    
    @property
    def is_quantity_based(self):
        """Check if this forecast type is quantity-based"""
        return self.forecast_type == 'deal_quantity'
    
    @property
    def is_revenue_amount_based(self):
        """Check if this forecast type uses actual deal amounts"""
        return self.forecast_type == 'deal_revenue_amount'
    
    @property
    def is_revenue_expected_based(self):
        """Check if this forecast type uses expected revenue amounts"""
        return self.forecast_type == 'deal_revenue_expected_amount'
    
    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('forecast:forecast_type_update_form_view', kwargs={'pk': self.pk})
    def get_delete_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('forecast:forecast_type_delete_view', kwargs={'pk': self.pk})
    
    
    
class ForecastCondition(HorillaCoreModel):
    """
    Defines filtering conditions for forecast types
    """
    forecast_type = models.ForeignKey(
        ForecastType, 
        on_delete=models.CASCADE, 
        related_name='conditions',
        verbose_name=_("Forecast Type")
    )
    
    field = models.CharField(max_length=100, verbose_name=_("Field Name"))
    operator = models.CharField(
        max_length=50, 
        choices=[
            ('equals', 'Equals'),
            ('not_equals', 'Not Equals'),
            ('contains', 'Contains'),
            ('not_contains', 'Does Not Contain'),
            ('starts_with', 'Starts With'),
            ('ends_with', 'Ends With'),
            ('greater_than', 'Greater Than'),
            ('greater_than_equal', 'Greater Than or Equal'),
            ('less_than', 'Less Than'),
            ('less_than_equal', 'Less Than or Equal'),
            ('is_empty', 'Is Empty'),
            ('is_not_empty', 'Is Not Empty'),
        ],
        verbose_name=_("Operator")
    )
    
    value = models.CharField(max_length=255, blank=True, verbose_name=_("Value"))
    
    logical_operator = models.CharField(
        max_length=3, 
        choices=[('and', 'AND'), ('or', 'OR')], 
        default='and',
        verbose_name=_("Logical Operator")
    )
    
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    
    class Meta:
        verbose_name = _("Forecast Condition")
        verbose_name_plural = _("Forecast Conditions")
        ordering = ['order', 'created_at']
        
    def __str__(self):
        return f"{self.forecast_type.name} - {self.field} {self.operator} {self.value}"

class Forecast(HorillaCoreModel):
    """
    Main forecast model that represents a forecast for a specific period/user/type
    """
    FORECAST_STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_("Forecast Name"))
    forecast_type = models.ForeignKey(
        ForecastType, 
        on_delete=models.CASCADE, 
        verbose_name=_("Forecast Type")
    )
    
    period = models.ForeignKey(
        Period, 
        on_delete=models.CASCADE,
        verbose_name=_("Period"),
        null=True,
        blank=True
    )
    quarter = models.ForeignKey(
        Quarter, 
        on_delete=models.CASCADE,
        verbose_name=_("Quarter"),
        null=True,
        blank=True
    )
    fiscal_year = models.ForeignKey(
        FiscalYearInstance,  
        on_delete=models.CASCADE,
        verbose_name=_("Fiscal Year")
    )
    
    owner = models.ForeignKey(
        HorillaUser, 
        on_delete=models.CASCADE,
        verbose_name=_("Forecast Owner")
    )
    
    # Revenue-based fields (for Deal Revenue forecasts)
    target_amount = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Target Amount")
    )
    pipeline_amount = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Pipeline Amount"),
        null=True,
        blank=True
    )
    best_case_amount = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Best Case Amount"),
        null=True,
        blank=True
    )
    commit_amount = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Commit Amount"),
        null=True,
        blank=True
    )
    closed_amount = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Closed Amount"),
        null=True,
        blank=True
    )
    actual_amount = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Actual Amount"),
        null=True,
        blank=True
    )
    
    target_quantity = models.IntegerField(
        default=0,
        verbose_name=_("Target Quantity"),
        null=True, blank=True,
    )
    pipeline_quantity = models.IntegerField(
        default=0,
        verbose_name=_("Pipeline Quantity"),
        null=True, blank=True,
    )
    best_case_quantity = models.IntegerField(
        default=0,
        verbose_name=_("Best Case Quantity"),
        null=True, blank=True,
    )
    commit_quantity = models.IntegerField(
        default=0,
        verbose_name=_("Commit Quantity"),
        null=True, blank=True,
    )
    closed_quantity = models.IntegerField(
        default=0,
        verbose_name=_("Closed Quantity"),
        null=True, blank=True,
    )
    actual_quantity = models.IntegerField(
        default=0,
        verbose_name=_("Actual Quantity"),
        null=True, blank=True,
    )
    
    status = models.CharField(
        max_length=20,
        choices=FORECAST_STATUS_CHOICES,
        default='draft',
        verbose_name=_("Status")
    )
    
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Submitted At"))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))
    approved_by = models.ForeignKey(
        HorillaUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_forecasts',
        verbose_name=_("Approved By")
    )
    
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        verbose_name = _("Forecast")
        verbose_name_plural = _("Forecasts")
        ordering = ['-created_at']
    
    def __str__(self):
        if self.period:
            return f"{self.name} - {self.period} - {self.owner}"
        elif self.quarter:
            return f"{self.name} - {self.quarter} - {self.owner}"
        else:
            return f"{self.name} - {self.fiscal_year} - {self.owner}"
    
    @property
    def achievement_percentage(self):
        """Calculate achievement percentage based on forecast type"""
        if self.forecast_type.is_quantity_based:
            if self.target_quantity and self.target_quantity > 0:
                return (self.actual_quantity / self.target_quantity) * 100
        else:  # Revenue-based (both amount and expected_amount)
            if self.target_amount and self.target_amount > 0:
                return (self.actual_amount / self.target_amount) * 100
        return 0

    @property
    def performance_percentage(self):
        """Alias for achievement_percentage for backward compatibility"""
        return self.achievement_percentage

    @property
    def gap_amount(self):
        """Calculate gap between target and actual (for revenue forecasts)"""
        if self.forecast_type.is_revenue_based:
            return self.target_amount - self.actual_amount
        return 0

    @property
    def gap_quantity(self):
        """Calculate gap between target and actual (for quantity forecasts)"""
        if self.forecast_type.is_quantity_based:
            return self.target_quantity - self.actual_quantity
        return 0

    @property
    def gap_percentage(self):
        """Calculate gap percentage based on forecast type"""
        if self.forecast_type.is_quantity_based:
            if self.target_quantity and self.target_quantity > 0:
                return ((self.target_quantity - self.actual_quantity) / self.target_quantity) * 100
        else:  # Revenue-based
            if self.target_amount and self.target_amount > 0:
                return ((self.target_amount - self.actual_amount) / self.target_amount) * 100
        return 0

    @property
    def closed_percentage(self):
        """Calculate closed percentage based on forecast type"""
        if self.forecast_type.is_quantity_based:
            if self.target_quantity and self.target_quantity > 0:
                return (self.closed_quantity / self.target_quantity) * 100
        else:  # Revenue-based
            if self.target_amount and self.target_amount > 0:
                return (self.closed_amount / self.target_amount) * 100
        return 0

    @property
    def closed_deals_count(self):
        """Get count of closed deals for this forecast period"""
        if not self.period:
            return 0
        
        return Opportunity.objects.filter(
            owner=self.owner,
            close_date__range=[self.period.start_date, self.period.end_date],
            stage__stage_type='won'
        ).count()

    # Enhanced display properties that work with all forecast types
    @property
    def display_target(self):
        """Return appropriate target value based on forecast type"""
        if self.forecast_type.is_quantity_based:
            return f"{self.target_quantity} deals"
        else:
            return f"{self.target_amount}"

    @property
    def display_actual(self):
        """Return appropriate actual value based on forecast type"""
        if self.forecast_type.is_quantity_based:
            return f"{self.actual_quantity} deals"
        else:
            return f"{self.actual_amount}"

    @property
    def display_pipeline(self):
        """Return appropriate pipeline value based on forecast type"""
        if self.forecast_type.is_quantity_based:
            return f"{self.pipeline_quantity} deals"
        else:
            return f"{self.pipeline_amount}"

    @property
    def display_commit(self):
        """Return appropriate commit value based on forecast type"""
        if self.forecast_type.is_quantity_based:
            return f"{self.commit_quantity} deals"
        else:
            return f"{self.commit_amount}"

    @property
    def display_best_case(self):
        """Return appropriate best case value based on forecast type"""
        if self.forecast_type.is_quantity_based:
            return f"{self.best_case_quantity} deals"
        else:
            return f"{self.best_case_amount}"

    @property
    def display_closed(self):
        """Return appropriate closed value based on forecast type"""
        if self.forecast_type.is_quantity_based:
            return f"{self.closed_quantity} deals"
        else:
            return f"{self.closed_amount}"

    def calculate_amounts_from_opportunities(self):
        """
        Calculate forecast amounts/quantities based on opportunities in the period.
        """
        from horilla_crm.forecast.utils import ForecastCalculator

        calculator = ForecastCalculator()
        calculator.calculate_amounts_from_opportunities_fixed(self)
        
        
    
    def save(self, *args, **kwargs):
        if not self.pk: 
            self.calculate_amounts_from_opportunities()
        
        super().save(*args, **kwargs)


class ForecastTarget(HorillaCoreModel):
    """
    Simplified forecast target model with ForecastType foreign key.
    Supports period-based targets only.
    """

    # User Assignment
    assigned_to = models.ForeignKey(
        HorillaUser,
        on_delete=models.CASCADE,
        verbose_name=_("Assigned User"),
        related_name='forecast_targets'
    )

    # Role (for organizational hierarchy)
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name=_("Role"),
        related_name="forecast_targets",
        null=True,
        blank=True
    )

    forcasts_type = models.ForeignKey(
        ForecastType,  # Assuming ForecastType is in the same app
        on_delete=models.CASCADE,
        verbose_name=_("Forecast Type"),
        related_name="forecast_targets"
    )

    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        verbose_name=_("Forecast Period"),
        related_name="forecast_targets"
    )

    # Target amount
    target_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_("Target"),
        help_text=_("Target amount (revenue or quantity)")
    )

    # Currency (for revenue targets)
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name=_("Currency"),
        help_text=_("Currency code (e.g., USD, EUR, INR)")
    )

    # Current achievement (auto-calculated)
    current_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("Current Achievement"),
        help_text=_("Current achieved amount (auto-calculated)")
    )

 

    class Meta:
        verbose_name = _("Forecast Target")
        verbose_name_plural = _("Forecast Targets")
        ordering = ['-created_at']
        unique_together = [
            ['assigned_to', 'period', 'forcasts_type'],
        ]

    def __str__(self):
        user_name = self.assigned_to.get_full_name() if self.assigned_to else "Unassigned"
        return f"{user_name} - {self.period.name} - {self.forcasts_type.name}"

    @property
    def achievement_percentage(self):
        """Calculate achievement percentage"""
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100

    @property
    def is_achieved(self):
        """Check if target is achieved"""
        return self.current_amount >= self.target_amount

    def get_manager_name(self):
        """Get manager name from role hierarchy"""
        if self.role and hasattr(self.role, 'manager'):
            return self.role.manager.get_full_name()
        return None

    @property
    def is_revenue_target(self):
        """Check if this is a revenue-based target"""
        return self.forcasts_type.is_revenue_based

    @property
    def is_quantity_target(self):
        """Check if this is a quantity-based target"""
        return self.forcasts_type.is_quantity_based
    
    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('forecast:forecast_target_update_form_view', kwargs={'pk': self.pk})
    
    def get_delete_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy('forecast:forecast_target_delete_view', kwargs={'pk': self.pk})
    
    
    

class ForecastTargetUser(HorillaCoreModel):
    """
    Model to store individual user targets when using 'each' split option for role-based targets.
    """
    forecast_target = models.ForeignKey(
        ForecastTarget,
        on_delete=models.CASCADE,
        related_name='user_targets',
        verbose_name=_("Forecast Target")
    )
    user = models.ForeignKey(
        HorillaUser,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name='individual_forecast_targets'
    )
    
    revenue_target = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("User Revenue Target"),
        help_text=_("Individual revenue target for this user")
    )
    quantity_target = models.IntegerField(
        default=0,
        verbose_name=_("User Quantity Target"),
        help_text=_("Individual quantity target for this user")
    )
    
    # Achievement tracking for individual user
    current_revenue = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("Current Revenue Achieved"),
        help_text=_("Current achieved revenue for this user")
    )
    current_quantity = models.IntegerField(
        default=0,
        verbose_name=_("Current Quantity Achieved"),
        help_text=_("Current achieved quantity for this user")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    class Meta:
        verbose_name = _("Forecast Target User")
        verbose_name_plural = _("Forecast Target Users")
        unique_together = ['forecast_target', 'user']
        
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.forecast_target.name}"

class ForecastTargetHistory(HorillaCoreModel):
    """
    Track historical changes to forecast targets for auditing and trend analysis
    """
    ACTION_CHOICES = [
        ('created', _('Created')),
        ('updated', _('Updated')),
        ('achieved', _('Achieved')),
        ('missed', _('Missed')),
    ]
    
    target = models.ForeignKey(
        ForecastTarget,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_("Forecast Target")
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name=_("Action")
    )
    
    # Snapshot of values at the time of change
    revenue_target_snapshot = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Revenue Target Snapshot")
    )
    quantity_target_snapshot = models.IntegerField(
        default=0,
        verbose_name=_("Quantity Target Snapshot")
    )
    current_revenue_snapshot = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        default=0,
        verbose_name=_("Current Revenue Snapshot")
    )
    current_quantity_snapshot = models.IntegerField(
        default=0,
        verbose_name=_("Current Quantity Snapshot")
    )
    
    changed_by = models.ForeignKey(
        HorillaUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Changed By")
    )
    
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        verbose_name = _("Forecast Target History")
        verbose_name_plural = _("Forecast Target Histories")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.target} - {self.get_action_display()} - {self.created_at}"

class ForecastHistory(HorillaCoreModel):
    """
    Track changes in forecast values over time
    """
    forecast = models.ForeignKey(
        Forecast,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_("Forecast")
    )
    
    previous_pipeline_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    previous_best_case_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    previous_commit_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    previous_closed_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    
    # New values
    new_pipeline_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    new_best_case_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    new_commit_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    new_closed_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    
    change_reason = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Change Reason")
    )
    
    changed_by = models.ForeignKey(
        HorillaUser,
        on_delete=models.CASCADE,
        verbose_name=_("Changed By")
    )
    
    class Meta:
        verbose_name = _("Forecast History")
        verbose_name_plural = _("Forecast History")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.forecast} - {self.created_at}"
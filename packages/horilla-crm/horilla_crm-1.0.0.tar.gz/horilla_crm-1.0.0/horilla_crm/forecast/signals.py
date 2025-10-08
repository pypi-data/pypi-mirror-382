from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

# Define your forecasts signals here
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from horilla_core.models import Period
from horilla_crm.opportunities.models import Opportunity
from horilla_crm.forecast.utils import ForecastCalculator


@receiver(post_save, sender=Opportunity)
def update_forecast_on_opportunity_save(sender, instance, created, **kwargs):
    """
    Automatically update forecasts when an opportunity is saved
    This keeps forecasts in sync with opportunity changes - just like Salesforce
    """
    if instance.close_date and instance.owner:
        try:
            period = Period.objects.filter(
                start_date__lte=instance.close_date,
                end_date__gte=instance.close_date
            ).first()
            
            if period:
                calculator = ForecastCalculator(
                    user=instance.owner,
                    fiscal_year=period.quarter.fiscal_year
                )
                calculator.generate_forecasts_for_user(instance.owner)
        except:
            pass  


@receiver(post_delete, sender=Opportunity)
def update_forecast_on_opportunity_delete(sender, instance, **kwargs):
    """
    Update forecasts when an opportunity is deleted
    """
    if instance.close_date and instance.owner:
        try:
            period = Period.objects.filter(
                start_date__lte=instance.close_date,
                end_date__gte=instance.close_date
            ).first()
            
            if period:
                calculator = ForecastCalculator(
                    user=instance.owner,
                    fiscal_year=period.quarter.fiscal_year
                )
                calculator.generate_forecasts_for_user(instance.owner)
        except:
            pass
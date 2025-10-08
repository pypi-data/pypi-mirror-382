"""
Models for the Leads module.

This file defines the database models related to leads in the CRM application.
These models represent the structure of lead-related data and include any
relationships, constraints, and behaviors.
"""

from auditlog.registry import auditlog
from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from horilla_core.models import Company, HorillaUser, HorillaCoreModel, MultipleCurrency
from horilla_core.utils import compute_score
from horilla_utils.methods import render_template
from django.utils.translation import gettext_lazy as _
from colorfield.fields import ColorField
from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.db.models.signals import pre_save


class LeadStatus(HorillaCoreModel):
    """
    Lead Status model
    """

    name = models.CharField(max_length=100, verbose_name=_("Status Name"))
    order = models.IntegerField(default=0, verbose_name=_("Status Order"))
    color = ColorField(default="#f39022", verbose_name=_("Status Color"))
    is_final = models.BooleanField(default=False, verbose_name=_("Is Final Stage"))
    probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Probability"),
        help_text="Default probability percentage for this stage",
    )

    # duration = models.IntegerField(default=0,verbose_name="duration in days")

    class Meta:
        verbose_name = _("Lead Stage")
        verbose_name_plural = _("Lead Stages")
        ordering = ["order"]

    def __str__(self):
        return str(self.name)

    def is_final_col(self):
        """Returns the HTML for the is_final column in the list view."""
        html = render_template(
            path="lead_status/is_final_col.html",
            context={"instance": self},
        )
        return mark_safe(html)

    def clean(self):
        if self.order < 0:
            raise ValidationError(_("Order must be a non-negative integer."))

    def save(self, *args, **kwargs):
        with transaction.atomic():
            previous_final = None
            if self.is_final:
                # Identify and unset the current final stage for the company
                previous_final = (
                    LeadStatus.objects.filter(is_final=True, company=self.company)
                    .exclude(pk=self.pk)
                    .first()
                )
                if previous_final:
                    LeadStatus.objects.filter(pk=previous_final.pk).update(
                        is_final=False
                    )

            if self.pk is None:
                # For new stages, use provided order or next available order
                if not self.order:
                    self.order = self.get_next_order_for_company(self.company)
                self._desired_position = self.order if not self.is_final else None
            else:
                original = LeadStatus.objects.get(pk=self.pk)
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
            LeadStatus.objects.filter(company=self.company).order_by("order", "pk")
        )

        final_statuses = [s for s in company_statuses if s.is_final]
        non_final_statuses = [s for s in company_statuses if not s.is_final]

        if len(final_statuses) > 1:
            if self.is_final and self in final_statuses:
                final_statuses = [self]
            else:
                final_statuses = final_statuses[:1]
            for status in [
                s for s in company_statuses if s.is_final and s not in final_statuses
            ]:
                LeadStatus.objects.filter(pk=status.pk).update(is_final=False)

        if hasattr(self, "_desired_position") and self._desired_position is not None:
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
                LeadStatus.objects.filter(pk=status.pk).update(order=i)

        if hasattr(self, "_desired_position"):
            delattr(self, "_desired_position")

    @receiver(post_delete, sender="leads.LeadStatus")
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
                    LeadStatus.objects.filter(company=company).order_by("order")
                )
                for i, status in enumerate(remaining_statuses, 1):
                    LeadStatus.objects.filter(pk=status.pk).update(order=i)
                if (
                    was_final
                    and remaining_statuses
                    and not any(s.is_final for s in remaining_statuses)
                ):
                    last_stage = remaining_statuses[-1]
                    LeadStatus.objects.filter(pk=last_stage.pk).update(is_final=True)
            except Company.DoesNotExist:
                return

    @classmethod
    def get_next_order_for_company(cls, company):
        """
        Get the next available order number for a company, just before final stage
        """
        max_order = cls.objects.filter(company=company, is_final=False).aggregate(
            max_order=models.Max("order")
        )["max_order"]
        return (max_order or 0) + 1

    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy("leads:edit_lead_stage", kwargs={"pk": self.pk})

    def get_delete_url(self):
        """
        This method to get delete url
        """
        return reverse_lazy("leads:delete_lead_stage", kwargs={"pk": self.pk})


class Lead(HorillaCoreModel):
    """
    Lead Model
    """

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

    INDUSTRY_CHOICES = [
        ("finance", _("Finance")),
        ("healthcare", _("Healthcare")),
        ("manufacturing", _("Manufacturing")),
        ("agriculture", _("Agriculture")),
        ("construction", _("Construction")),
        ("banking", _("Banking")),
        ("education", _("Education")),
        ("insurance", _("Insurance")),
        ("other", _("Other")),
    ]

    lead_owner = models.ForeignKey(
        HorillaUser,
        on_delete=models.PROTECT,
        default="",
        verbose_name=_("Lead Owner"),
        related_name="lead",
    )
    title = models.CharField(max_length=100, blank=True, verbose_name=_("Title"))
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    email = models.EmailField(validators=[EmailValidator()], verbose_name=_("Email"))
    contact_number = models.CharField(
        max_length=100, blank=True, verbose_name=_("Contact Number")
    )
    fax = models.CharField(max_length=100, blank=True, verbose_name=_("Fax"))
    lead_currency = models.ForeignKey(
        MultipleCurrency,
        on_delete=models.PROTECT,
        default="",
        null=True,
        blank=True,
        verbose_name=_("Lead Currency"),
    )
    lead_source = models.CharField(
        max_length=100, choices=LEAD_SOURCES, verbose_name=_("Lead Source")
    )
    lead_status = models.ForeignKey(
        LeadStatus,
        on_delete=models.PROTECT,
        related_name="lead",
        verbose_name=_("Lead Status"),
    )
    lead_company = models.CharField(max_length=100, verbose_name=_("Lead Company"))
    no_of_employees = models.IntegerField(
        null=True, blank=True, verbose_name=_("Total Employees")
    )
    industry = models.CharField(
        max_length=100, choices=INDUSTRY_CHOICES, verbose_name=_("Industry")
    )
    annual_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Annual Revenue"),
    )
    city = models.CharField(blank=True, max_length=100, verbose_name=_("City"))
    state = models.CharField(blank=True, max_length=100, verbose_name=_("State"))
    country = models.CharField(blank=True, max_length=100, verbose_name=_("Country"))
    zip_code = models.CharField(max_length=100, blank=True, verbose_name=_("Zip"))
    requirements = models.TextField(blank=True, verbose_name=_("Requirements"))
    is_convert = models.BooleanField(default=False)
    lead_score = models.IntegerField(default=0, verbose_name=_("Lead Score"))

    OWNER_FIELDS = ["lead_owner"]

    class Meta:
        verbose_name = _("Lead")
        verbose_name_plural = _("Leads")

    def __str__(self):
        return f"{str(self.title)}-{self.id}"

    def test(self):
        return "test"

    def actions(self):
        """
        This method for get custom column for action.
        """

        return render_template(
            path="actions.html",
            context={"instance": self},
        )

    @property
    def get_annual_revenue_calc(self):
        """
        This method to get annual revenue
        """
        return self.annual_revenue * 3

    LEAD_PROPERTY_LABELS = {"annual_revenue_calc": _("Annual Revenue 3x")}

    DYNAMIC_METHODS = ["get_edit_url"]

    def get_detail_url(self):
        """
        This method to get delete url
        """
        return reverse_lazy("leads:leads_detail", kwargs={"pk": self.pk})

    def get_delete_url(self):
        """
        This method to get delete url
        """
        return reverse_lazy("leads:leads_delete", kwargs={"pk": self.pk})

    def get_edit_url(self):
        """
        This method to get edit url
        """
        return reverse_lazy("leads:leads_edit_single", kwargs={"pk": self.pk})

    def get_change_owner_url(self):
        """
        This method to get change owner url
        """
        return reverse_lazy("leads:lead_change_owner", kwargs={"pk": self.pk})

    def get_lead_convert_url(self):
        """
        This method to get change owner url
        """
        return reverse_lazy("leads:convert_lead", kwargs={"pk": self.pk})


@receiver(pre_save, sender=Lead)
def update_lead_score(sender, instance, **kwargs):
    instance.lead_score = compute_score(instance)
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horilla_core.models import HorillaUser, HorillaCoreModel

class UserCalendarPreference(HorillaCoreModel):
    CALENDAR_TYPES = (
        ('task', 'Task'),
        ('event', 'Event'),
        ('meeting', 'Meeting'),
        ('unavailability','Un Availability')
    )
    
    user =  models.ForeignKey(HorillaUser, on_delete=models.PROTECT,
        related_name='calendar_preferences',
        verbose_name=_("User")
    )
    calendar_type = models.CharField(max_length=20, choices=CALENDAR_TYPES, verbose_name=_("Calendar Type"))
    color = models.CharField(max_length=10, verbose_name=_("Color"))  # Hex color code
    is_selected = models.BooleanField(default=True, verbose_name=_("Is Selected"))  # New field for "Display This Only"
   
    class Meta:
        unique_together = ('user', 'calendar_type','company')  # One preference per user per calendar type
        verbose_name = _("User Calendar Preference")
        verbose_name_plural = _("User Calendar Preferences")

    def __str__(self):
        return f"{self.user.username} - {self.calendar_type} - {self.color} (Selected: {self.is_selected})"
    


class UserAvailability(HorillaCoreModel):
    user = models.ForeignKey(HorillaUser, on_delete=models.PROTECT,
        related_name="unavailable_periods",
        verbose_name=_("User")
    )
    from_datetime = models.DateTimeField(verbose_name=_("From"))
    to_datetime = models.DateTimeField(verbose_name=_("To"))
    reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Reason")
    )

    class Meta:
        verbose_name = _("User Unavailability")
        verbose_name_plural = _("User Unavailabilities")
        ordering = ['-from_datetime']
        indexes = [
            models.Index(fields=["user", "from_datetime", "to_datetime"]),
        ]

    def __str__(self):
        return f"{self.user} unavailable from {self.from_datetime} to {self.to_datetime}"

    def is_currently_unavailable(self):
        from django.utils import timezone
        now = timezone.now()
        return self.from_datetime <= now <= self.to_datetime
    
    def update_mark_unavailability_url(self):
         return reverse_lazy('timeline:update_mark_unavailability', kwargs={'pk': self.pk})
    

    def delete_mark_unavailability_url(self):
        return reverse_lazy('timeline:delete_mark_unavailability',kwargs={'pk': self.pk})

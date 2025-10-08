from django.db import models

# Create your activity models here.
"""
Models for the CRM utilities module.

This file defines the database models used in the CRM application.
These models represent the structure of the data and include any
relationships, constraints, and behaviors.
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horilla_core.models import HorillaUser, HorillaCoreModel

class Activity(HorillaCoreModel):
    ACTIVITY_TYPES = [
        ("event", "Event"),
        ("meeting", "Meeting"),
        ("task", "Task"),
        ("log_call", "Log Call"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
       
    ]
    TASK_PRIORITY_CHOICES = [
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]
    CALL_TYPE_CHOICES = [
        ("Inbound", "Inbound"),
        ("Outbound", "Outbound"),
    ]


    # Common fields from GeneralActivity
    subject = models.CharField(max_length=100, verbose_name=_("Subject"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, verbose_name=_("Activity Type"))
    source = models.CharField(max_length=100, blank=True, verbose_name=_("Source"))
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Related Content Type")
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Related Object ID"))
    related_object = GenericForeignKey("content_type", "object_id")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name=_("Status"))

    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Title"))
    start_datetime = models.DateTimeField(null=True, blank=True, verbose_name=_("Start Date"))
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name=_("End Date"))
    location = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Location"))
    is_all_day = models.BooleanField(default=False, verbose_name=_("All Day"))
    assigned_to = models.ManyToManyField(
        HorillaUser, related_name="assigned_activities",blank=True, verbose_name=_("Assigned To")
    )
    participants = models.ManyToManyField(
        HorillaUser, related_name="activity_participants", null=True, blank=True, verbose_name=_("Participants")
    )
    meeting_host = models.ForeignKey(
        HorillaUser, related_name="hosted_activities", on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Meeting Host")
    )
    owner = models.ForeignKey(
        HorillaUser, related_name="owned_activities", on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Activity Owner")
    )
    # Task-specific
    task_priority = models.CharField(max_length=50, choices=TASK_PRIORITY_CHOICES, null=True, blank=True, verbose_name=_("Priority"))
    due_datetime = models.DateTimeField(null=True, blank=True, verbose_name=_("Due Date"))
    recipient_email = models.EmailField(null=True, blank=True, verbose_name=_("Recipient Email"))


    # LogCall-specific
    call_duration_display = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Call Duration"))
    call_duration_seconds = models.IntegerField(null=True, blank=True, verbose_name=_("Call Duration (Seconds)"))
    call_type = models.CharField(max_length=50, choices=CALL_TYPE_CHOICES, null=True, blank=True, verbose_name=_("Call Type"))
    notes = models.TextField(null=True, blank=True, verbose_name=_("Notes"))
    call_purpose = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Call Purpose"))

    OWNER_FIELDS = ["owner","assigned_to"]

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        indexes = [
            models.Index(fields=["activity_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["start_datetime"]),
            models.Index(fields=["due_datetime"]),
        ]

    def __str__(self):
        return self.subject or self.title or f"{self.activity_type} {self.pk}"

    def save(self, *args, **kwargs):
        if self.activity_type == "log_call" and self.call_duration_display:
            try:
                h, m, s = map(int, self.call_duration_display.split(":"))
                self.call_duration_seconds = h * 3600 + m * 60 + s
            except:
                self.call_duration_seconds = None
        super().save(*args, **kwargs)

    def get_detail_url(self):
        """
        This method to get detail url
        """
        return reverse_lazy('activity:activity_detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        url_map = {
            "event": "activity:event_update_form",
            "meeting": "activity:meeting_update_form",
            "task": "activity:task_update_form",
            # "email": "activity:event_update_form",
            "log_call": "activity:call_update_form",
        }
        return reverse_lazy(url_map[self.activity_type], kwargs={"pk": self.pk})
    
    def get_activity_edit_url(self):
        return reverse_lazy('activity:activity_edit_form', kwargs={"pk": self.pk})


    def get_delete_url(self):
        return reverse_lazy("activity:delete_activity", kwargs={"pk": self.pk})

    def get_start_date(self):
        if self.activity_type in ["event", "meeting"] and self.is_all_day:
            return "All Day Event"
        return self.start_datetime or self.due_datetime or self.created_at

    def get_end_date(self):
        if self.activity_type in ["event", "meeting"] and self.is_all_day:
            return "All Day Event"
        return self.end_datetime or self.due_datetime or self.created_at
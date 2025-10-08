from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from horilla_core.models import Company
from horilla_crm.leads.models import LeadStatus

# Define your leads signals here

# @receiver(post_save, sender=Company)
# def create_default_lead_stages(sender, instance, created, **kwargs):
#     """
#     Automatically create default lead stages for a company when it is created.
#     """
#     if created:
#         default_stages = [
#             {"name": "New", "order": 1,  "probability": 10, "is_final": False},
#             {"name": "Contacted", "order": 2, "probability": 30, "is_final": False},
#             {"name": "Qualified", "order": 3, "probability": 60, "is_final": False},
#             {"name": "Proposal", "order": 4,  "probability": 80, "is_final": False},
#             {"name": "Lost", "order": 5, "probability": 0, "is_final": False},
#             {"name": "Won", "order": 6,  "probability": 100, "is_final": True},
#         ]

#         for stage in default_stages:
#             LeadStatus.objects.create(
#                 company=instance,
#                 name=stage["name"],
#                 order=stage["order"],
#                 probability=stage["probability"],
#                 is_final=stage["is_final"],
#             )
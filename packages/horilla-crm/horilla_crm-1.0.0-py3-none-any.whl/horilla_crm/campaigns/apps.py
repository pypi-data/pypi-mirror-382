from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _



class CampaignsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'horilla_crm.campaigns'
    label = "campaigns"  
    icon = "campaign.svg"
    verbose_name = _("Campaigns")
    url = reverse_lazy("campaigns:campaign_view")
    section = "sales"
    
    def ready(self):
        try:
            from django.urls import include, path
            from horilla.urls import urlpatterns
            from horilla.sidebar import register_sub_section
           
                
            urlpatterns.append(
                    path('campaigns/', include('horilla_crm.campaigns.urls')),
                )
            register_sub_section(
                self.section,
                self.verbose_name,
                self.icon,
                self.url,
                app_label=self.label,
                perm=["campaigns.view_campaign", "campaigns.view_own_campaign"],
            )
        
            from horilla_crm.campaigns import floating_menu
            
        except Exception as e:
            import logging

            logging.warning(f"CampaignsConfig.ready failed: {e}")
            pass
        super().ready()

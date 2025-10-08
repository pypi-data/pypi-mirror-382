from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class LeadsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'horilla_crm.leads'
    label = "leads"  
    icon = "leads.svg"
    verbose_name = _("Leads")
    url = reverse_lazy("leads:leads_view")
    section = "sales"
    
    def ready(self):
        try:
            # Auto-register this app's URLs and add to installed apps
            from django.urls import include, path
            from horilla.urls import urlpatterns
            from horilla_crm.leads import signals
            from horilla.sidebar import register_sub_section,register_section
            
            
            urlpatterns.append(
                    path('leads/', include('horilla_crm.leads.urls', namespace='leads')),
                )
            
            register_section(
                self.section,
                _("Sales"),
                reverse_lazy("leads:leads_view"),
                "sales.svg",
                position=1
            )

            register_sub_section(
                self.section,
                self.verbose_name,
                self.icon,
                self.url,
                app_label=self.label, 
                perm=["leads.view_lead", "leads.view_own_lead"],
            )
            from horilla_crm.leads import settings_menu,floating_menu
        except Exception as e:
            import logging

            logging.warning(f"LeadsConfig.ready failed: {e}")
            pass
        super().ready()

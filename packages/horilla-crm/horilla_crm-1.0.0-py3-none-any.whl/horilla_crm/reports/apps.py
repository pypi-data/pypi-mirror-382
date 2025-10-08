from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class Reports(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'horilla_crm.reports'
    label = "reports"  
    icon = "reports.svg"
    verbose_name = _("Reports")
    url = reverse_lazy("reports:reports_list_view")
    section = "analytics"
    
    def ready(self):
        try:
            from django.urls import include, path
            from horilla.urls import urlpatterns
            from horilla.sidebar import register_sub_section,register_section
           
                
            urlpatterns.append(
                    path('reports/', include('horilla_crm.reports.urls')),
                )
            
            register_section(
                self.section,
                _("Analytics"),
                reverse_lazy("reports:reports_list_view"),
                "data-analytics.svg",
                position=3
            )
            
            register_sub_section(
                self.section,
                self.verbose_name,
                self.icon,
                self.url,
                app_label=self.label,
                perm=["reports.view_report","reports.view_own_report"] 
            )
            
        except Exception as e:
            import logging
            logging.warning(f"Reports.ready failed: {e}")
            pass
            
        super().ready()

from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _



class DashboardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'horilla_crm.dashboards'
    label = "dashboards"  
    icon = "dashboards.svg"
    verbose_name = _("Dashboards")
    url = reverse_lazy("dashboards:dashboard_list_view")
    section = "analytics"
    
    def ready(self):
        try:
            # Auto-register this app's URLs and add to installed apps
            from django.urls import include, path
            from horilla.urls import urlpatterns
            from horilla.sidebar import register_sub_section,register_section

            # Add app URLs to main urlpatterns
            urlpatterns.append(
                    path('dashboards/', include('horilla_crm.dashboards.urls')),
                )
            
            register_section(
                "home",
                _("Home"),
                reverse_lazy("dashboards:home_view"),
                "home.svg",
                position=0
                )
            
                
            register_sub_section(
                self.section,
                self.verbose_name,
                self.icon,
                self.url,
                app_label=self.label, 
                perm=["dashboards.view_dashboard","dashboards.view_own_dashboard"]
            )
            
        except Exception as e:
            import logging

            logging.warning(f"DashboardsConfig.ready failed: {e}")
            pass
        super().ready()

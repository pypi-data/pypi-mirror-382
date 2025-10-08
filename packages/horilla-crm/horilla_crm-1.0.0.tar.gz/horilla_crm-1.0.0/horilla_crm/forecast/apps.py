from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _



class ForecastsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'horilla_crm.forecast'
    label = "forecast"  
    icon = "forecast.svg"
    verbose_name = _("Forecast")
    url = reverse_lazy("forecast:forecast_view")
    section = "sales"
    
    def ready(self):
        try:
            from django.urls import include, path
            from horilla.urls import urlpatterns
            from horilla_crm.forecast import signals
            from horilla.sidebar import register_sub_section
           
                
            urlpatterns.append(
                    path('forecast/', include('horilla_crm.forecast.urls')),
                )
            
            register_sub_section(
                self.section,
                self.verbose_name,
                self.icon,
                self.url,
                app_label=self.label, 
                perm=["forecast.view_forecast","forecast:view_own_forecast"]
            )
            from horilla_crm.forecast import settings_menu
            
        except Exception as e:
            import logging

            logging.warning(f"ForecastsConfig.ready failed: {e}")
            pass
            
        super().ready()

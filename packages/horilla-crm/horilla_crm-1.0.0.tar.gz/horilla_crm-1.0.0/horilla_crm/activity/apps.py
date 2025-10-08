from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _



class ActivityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'horilla_crm.activity'
    label = "activity"  
    icon = "activity.svg"
    verbose_name = _("Activities")
    url = reverse_lazy("activity:activity_view")
    section = "schedule"
    
    def ready(self):
        try:
            # Auto-register this app's URLs and add to installed apps
            from django.urls import include, path
            from horilla.urls import urlpatterns
            from horilla.sidebar import register_sub_section
           
                
            # Add app URLs to main urlpatterns
            urlpatterns.append(
                    path('activity/', include('horilla_crm.activity.urls')),
                )
            
            register_sub_section(
                self.section,
                self.verbose_name,
                self.icon,
                self.url,
                app_label=self.label, 
                perm=["activity.view_activity", "activity.view_own_activity"],
            )
            
        except Exception as e:
            import logging

            logging.warning(f"ActivityConfig.ready failed: {e}")
            pass
            
        super().ready()

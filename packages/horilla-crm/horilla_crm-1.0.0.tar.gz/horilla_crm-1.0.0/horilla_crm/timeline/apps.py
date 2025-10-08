from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _



class TimelineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'horilla_crm.timeline'
    label = "timeline"  
    icon = "calendar.svg"
    verbose_name = _("Calendar")
    url = reverse_lazy("timeline:calendar_view")
    section = "schedule"
    
    def ready(self):
        try:
            # Auto-register this app's URLs and add to installed apps
            from django.urls import include, path
            from horilla.urls import urlpatterns
            from horilla.sidebar import register_sub_section,register_section

           
                
            # Add app URLs to main urlpatterns
            urlpatterns.append(
                    path('timeline/', include('horilla_crm.timeline.urls')),
                )
            
            register_section(
                self.section,
                _("Schedule"),
                reverse_lazy("timeline:calendar_view"),
                "schedule.svg",
                position=4
            )

            register_sub_section(
                self.section,
                self.verbose_name,
                self.icon,
                self.url,
                app_label=self.label,
                # perm="timeline.view_calendar" 
            )
            
        except ImportError:
            # Handle errors silently to prevent app load failure
            pass
            
        super().ready()

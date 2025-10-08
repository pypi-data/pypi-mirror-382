from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _



class ContactsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'horilla_crm.contacts'
    label = "contacts"  
    icon = "contact.svg"
    verbose_name = _("Contacts")
    url = reverse_lazy("contacts:contacts_view")
    section = "people"
    
    def ready(self):
        try:
            from django.urls import include, path
            from horilla.urls import urlpatterns
            from horilla.sidebar import register_sub_section
           
                
            # Add app URLs to main urlpatterns
            urlpatterns.append(
                    path('contacts/', include('horilla_crm.contacts.urls')),
                )
            
            register_sub_section(
                self.section,
                self.verbose_name,
                self.icon,
                self.url,
                app_label=self.label, 
                perm=["contacts.view_contact","contacts.view_own_contact"]
            )
            
            from horilla_crm.contacts import floating_menu 
        except Exception as e:
            import logging

            logging.warning(f"ContactsConfig.ready failed: {e}")
            pass
            
        super().ready()

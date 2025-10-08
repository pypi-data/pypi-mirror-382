from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'horilla_crm.accounts'
    label = "accounts"  
    icon = "account.svg"
    verbose_name = _("Accounts")
    url = reverse_lazy("accounts:accounts_view")
    section = "people"  

    
    def ready(self):
        try:
            from django.urls import include, path
            from horilla.urls import urlpatterns
            from horilla.sidebar import register_sub_section,register_section
           
                
            urlpatterns.append(
                    path('accounts/', include('horilla_crm.accounts.urls')),
                )
            
            register_section(
                self.section,
                _("People"),
                reverse_lazy("accounts:accounts_view"),
                "customer.svg",
                position=2
            )
            
            register_sub_section(
                self.section,
                self.verbose_name,
                self.icon,
                self.url,
                app_label=self.label, 
                perm=["accounts.view_account","accounts.view_own_account"]
            )

            from horilla_crm.accounts import floating_menu
            
        except Exception as e:
            import logging

            logging.warning(f"AccountsConfig.ready failed: {e}")
            pass
            
        super().ready()

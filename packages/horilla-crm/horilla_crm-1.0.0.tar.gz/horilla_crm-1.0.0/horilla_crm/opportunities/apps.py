from django.apps import AppConfig
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class OpportunitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "horilla_crm.opportunities"
    label = "opportunities"
    icon = "opportunities.svg"
    verbose_name = _("Opportunities")
    url = reverse_lazy("opportunities:opportunities_view")
    section = "sales"

    def ready(self):
        from django.urls import include, path
        from horilla.urls import urlpatterns
        from horilla.sidebar import register_sub_section

        try:
            urlpatterns.append(
                path("opportunities/", include("horilla_crm.opportunities.urls")),
            )

            register_sub_section(
                self.section,
                self.verbose_name,
                self.icon,
                self.url,
                app_label=self.label,
                perm=[
                    "opportunities.view_opportunity",
                    "opportunities.view_own_opportunity",
                ],
            )
            from horilla_crm.opportunities import settings_menu, floating_menu
            from . import my_settings_menu

        except Exception as e:
            import logging

            logging.warning(f"OpportunitiesConfig.ready failed: {e}")
        super().ready()

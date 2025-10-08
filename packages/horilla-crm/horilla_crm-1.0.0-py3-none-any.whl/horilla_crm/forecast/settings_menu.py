from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horilla.settings_sidebar import register
from horilla_crm.forecast.models import ForecastTarget,ForecastType


@register
class ForecastSettings:
    title = _("Forecast")
    icon = "/assets/icons/growth.svg"
    items = [
        {
            "label": ForecastType()._meta.verbose_name,
            "url": reverse_lazy("forecast:forecast_type_view"),
            "hx-target": "#settings-content",
            "hx-push-url": "true",
            "hx-select": "#forecast-type-view",
            "hx-select-oob": "#settings-sidebar",
            "perm" : "forecast.view_forecasttype"
        },
        {
            "label": ForecastTarget()._meta.verbose_name,
            "url": reverse_lazy("forecast:forecast_target_view"),
            "hx-target": "#settings-content",
            "hx-push-url": "true",
            "hx-select": "#forecast-target-view",
            "hx-select-oob": "#settings-sidebar",
            "perm" : "forecast.view_forecasttarget"
        },
        
    ]

import django_filters

from horilla_crm.accounts.models import Account
from horilla_generics.filters import HorillaFilterSet

# Define your accounts filters here
class AccountFilter(HorillaFilterSet):
    class Meta:
        model = Account
        fields ='__all__'
        exclude = ['additional_info']
        search_fields = ['name']
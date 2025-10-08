import django_filters
from .models import Contact
from horilla_generics.filters import HorillaFilterSet
# Define your contacts filters here

class ContactFilter(HorillaFilterSet):
    """
    Filter class for contact model
    """
    class Meta:
        model = Contact
        fields = '__all__'
        exclude = ['additional_info']
        search_fields = ['first_name','last_name','email']

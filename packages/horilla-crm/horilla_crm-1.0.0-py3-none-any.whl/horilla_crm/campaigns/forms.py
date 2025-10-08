from django import forms
from django.urls import reverse_lazy
from horilla_core.mixins import OwnerQuerysetMixin
from horilla_generics.forms import HorillaModelForm, HorillaMultiStepForm
from .models import Campaign, CampaignMember
from django.utils.translation import gettext_lazy as _

class CampaignFormClass(OwnerQuerysetMixin,HorillaMultiStepForm):
    """
    form class for campaign
    """
    class Meta:
        model = Campaign
        fields = '__all__'
    
    step_fields = {
        1:  ['campaign_owner', 'campaign_name','parent_campaign' ,'campaign_type', 'status', 'start_date', 'end_date' ,'campaign_currency'],
        2:  ['expected_revenue', 'budget_cost', 'actual_cost', 'expected_response'],
        3:  ['number_sent', 'description']
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make created_by and updated_by optional in intermediate steps
        if self.current_step < len(self.step_fields):
            self.fields['created_by'].required = False
            self.fields['updated_by'].required = False


class CampaignMemberForm(HorillaModelForm):
    class Meta:
        model = CampaignMember
        fields = ['member_type', 'campaign', 'lead', 'contact', 'member_status']
        widgets = {
            'member_type': forms.Select(attrs={
                'class': 'form-select',
                'hx-get': '/campaigns/add-campaign-members/',
                'hx-trigger': 'change',
                'hx-target': '#campaignmember-form-view-container',
                'hx-include': '#id_campaign',
                'hx-swap': 'outerHTML',
            }),
            'campaign': forms.HiddenInput(),
            'is_active': forms.HiddenInput(),
            'company': forms.HiddenInput(),


        }
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.instance.pk:
                self.fields['member_type'].widget.attrs.update({
                    'hx-get': f'/campaigns/edit-added-campaign-members/{self.instance.pk}'
                })
            else:
                self.fields['member_type'].widget.attrs.update({
                    'hx-get': '/campaigns/add-campaign-members'
                })

            member_type = self.data.get('member_type') or self.initial.get('member_type')
            if member_type is None:
                self.fields['lead'].widget = forms.HiddenInput()
                self.fields['contact'].widget = forms.HiddenInput()
            if member_type == 'lead':
                self.fields['contact'].widget = forms.HiddenInput()
            elif member_type == 'contact':
                self.fields['lead'].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.type = self.cleaned_data['member_type']
        if commit:
            instance.save() 
        return instance
    

class ChildCampaignForm(forms.Form):
    """
    Form to select an existing campaign and assign it as a child campaign.
    """

    campaign = forms.ModelChoiceField(
        queryset=Campaign.objects.none(), 
        label=_("Select Campaign"),
        widget=forms.Select(attrs={
            'class': 'select2-pagination w-full text-sm',  
            'data-placeholder': 'Select Campaign',
            'data-url': reverse_lazy(
                    f'horilla_generics:model_select2',
                    kwargs={'app_label': 'campaigns', 'model_name': 'Campaign'}
                ),
                'data-placeholder': f'Select Campaign',
                'data-field-name': 'campaign',
                'id': f'id_campaign'
        }),
        help_text=_("Select campaign"),
    )
    
    parent_campaign = forms.ModelChoiceField(
        queryset=Campaign.objects.all(),
        required=False,
        widget=forms.HiddenInput()  
    )
    
    def __init__(self, *args, **kwargs):
        
        self.request = kwargs.pop('request', None)
        
        generic_attrs = ['full_width_fields', 'dynamic_create_fields', 'hidden_fields']
        for attr in generic_attrs:
            kwargs.pop(attr, None)
        
        
        super().__init__(*args, **kwargs)
        
        self.setup_campaign_queryset()
        
    
    def setup_campaign_queryset(self):
        """
        Set up the campaign queryset based on the request parameters.
        """
        if not self.request:
            self.fields['campaign'].queryset = Campaign.objects.all()
            return
            
        parent_id = self.request.GET.get('id')
        if not parent_id:
            self.fields['campaign'].queryset = Campaign.objects.all()
            return
            
        try:
            parent_campaign = Campaign.objects.get(pk=parent_id)
            
            queryset = Campaign.objects.all()
            queryset = queryset.exclude(id=parent_id)
            
            queryset = queryset.filter(parent_campaign__isnull=True)
            descendant_ids = self.get_descendant_ids(parent_campaign)
            if descendant_ids:
                queryset = queryset.exclude(id__in=descendant_ids)
            
            self.fields['campaign'].queryset = queryset
            
        except Campaign.DoesNotExist:
            self.fields['campaign'].queryset = Campaign.objects.filter(parent_campaign__isnull=True)
    
    def get_descendant_ids(self, campaign):
        """
        Get all descendant IDs of an campaign to prevent circular references.
        """
        descendant_ids = []
        children = Campaign.objects.filter(parent_campaign=campaign)
        for child in children:
            descendant_ids.append(child.id)
            descendant_ids.extend(self.get_descendant_ids(child))
        return descendant_ids
    
    def clean_campaign(self):
        """
        Validate the selected campaign.
        """
        campaign = self.cleaned_data.get('campaign')
        if not campaign:
            raise forms.ValidationError(_("Please select campaign."))
        
        if campaign.parent_campaign:
            raise forms.ValidationError(
                _("This campaign already has a parent campaign assigned.")
            )
        
        # Get parent from hidden field instead of request
        parent_campaign = self.cleaned_data.get('parent_campaign')
        if parent_campaign and str(campaign.id) == str(parent_campaign.id):
            raise forms.ValidationError(
                _("An campaign cannot be its own parent.")
            )
        
        return campaign
    
    def clean(self):
        cleaned_data = super().clean()
        campaign = cleaned_data.get('campaign')
        
        if not campaign:
            raise forms.ValidationError(_("Please select a valid campaign."))
        
        return cleaned_data        

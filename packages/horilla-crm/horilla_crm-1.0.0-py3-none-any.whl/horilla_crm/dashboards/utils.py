import uuid
import json
from django.db.models import  Count
from horilla_crm.accounts.models import Account
from horilla_crm.campaigns.models import Campaign
from horilla_crm.contacts.models import Contact
from django.core.paginator import Paginator
from horilla_crm.dashboards.models import Dashboard
from horilla_crm.leads.models import Lead
from horilla_crm.opportunities.models import Opportunity
from horilla_utils.middlewares import _thread_local

import logging
logger = logging.getLogger(__name__)



def dashboard_context(request):
    """
    Add dashboard-related context to all templates
    """
    context = {}
    
    if request.user.is_authenticated:
        default_dashboard = Dashboard.get_default_dashboard(request.user)
        context['has_default_dashboard'] = default_dashboard is not None
        context['default_dashboard'] = default_dashboard
    
    return context


class DefaultDashboardGenerator:
    """
    Simple dashboard generator for specific predefined models
    """
    
    def __init__(self, user, company=None):
        self.user = user
        self.company = company
        
        try:
            
            self.models = [
                {'model': Lead, 'name': 'Leads', 'icon': 'fa-user-plus', 'color': 'blue'},
                {'model': Contact, 'name': 'Contacts', 'icon': 'fa-address-book', 'color': 'green'},
                {'model': Opportunity, 'name': 'Opportunities', 'icon': 'fa-handshake', 'color': 'purple'},
                {'model': Account, 'name': 'Accounts', 'icon': 'fa-building', 'color': 'indigo'},
                {'model': Campaign, 'name': 'Campaigns', 'icon': 'fa-bullhorn', 'color': 'orange'},
            ]
        except ImportError:
            logger.warning("CRM models not found, using empty model list")
            self.models = []
    
    
    def get_queryset(self, model_class):
        """Get filtered queryset for a model"""
        queryset = model_class.objects.all()
        
        if hasattr(model_class, 'company') and self.company:
            queryset = queryset.filter(company=self.company)
        elif hasattr(model_class, 'user') and self.user:
            queryset = queryset.filter(user=self.user)
        elif hasattr(model_class, 'created_by') and self.user:
            queryset = queryset.filter(created_by=self.user)
            
        return queryset
    

    def generate_kpi_data(self):
        """Generate simple count KPIs"""
        kpis = []
        
        for model_info in self.models[:4]:  
            try:
                model_class = model_info['model']
                # Get the app label and model name for permission check
                app_label = model_class._meta.app_label
                model_name = model_class._meta.model_name
                permission = f"{app_label}.view_{model_name}"
                if self.user.has_perm(permission):
                    count = self.get_queryset(model_info['model']).count()
                    kpis.append({
                        'title': f"Total {model_info['name']}",
                        'value': count,
                        'icon': model_info['icon'],
                        'color': model_info['color'],
                        'type': 'count'
                    })
            except Exception as e:
                logger.warning(f"Failed to generate KPI for {model_info['name']}: {e}")
                
        return kpis
    

    def generate_chart_data(self):
        """Generate business-specific filtered charts"""
        charts = []
        
        for model_info in self.models[:5]:  
            try:
                queryset = self.get_queryset(model_info['model'])
                if queryset.count() == 0:
                    continue

                model_name = model_info['model'].__name__.lower()
                model_class = model_info['model']
                app_label = model_class._meta.app_label
                permission = f"{app_label}.view_{model_name}"
                
                
                if model_name == 'lead':
                    chart = self.create_lead_charts(queryset, model_info)
                elif model_name == 'opportunity':
                    chart = self.create_opportunity_charts(queryset, model_info)
                elif model_name == 'campaign':
                    chart = self.create_campaign_charts(queryset, model_info)
                elif model_name == 'contact':
                    chart = self.create_contact_charts(queryset, model_info)
                else:
                    chart = self.create_generic_chart(queryset, model_info)
                
                if self.user.has_perm(permission):
                    if chart:
                        charts.append(chart)
                        
            except Exception as e:
                logger.warning(f"Failed to generate chart for {model_info['name']}: {e}")
                
        return charts
    

    def get_date_field(self, model_class):
        """Get the first date field from model"""
        for field in model_class._meta.fields:
            if field.get_internal_type() in ['DateField', 'DateTimeField']:
                return field.name
        return None
    
    
    def create_lead_charts(self, queryset, model_info):
        """Create lead-specific charts with business conditions"""
        try:
            if hasattr(queryset.model, 'lead_source') or hasattr(queryset.model, 'source'):
                source_field = 'lead_source' if hasattr(queryset.model, 'lead_source') else 'source'
                source_data = queryset.values(source_field).annotate(count=Count('id')).order_by('-count')
                
                if source_data.exists():
                    labels = [item[source_field] or 'Unknown' for item in source_data]
                    data = [item['count'] for item in source_data]
                    
                    return {
                        'title': 'Leads by Source',
                        'type': 'funnel',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': 'Lead Source'
                        }
                    }
            
            if hasattr(queryset.model, 'is_converted') or hasattr(queryset.model, 'converted'):
                convert_field = 'is_converted' if hasattr(queryset.model, 'is_converted') else 'converted'
                convert_data = queryset.values(convert_field).annotate(count=Count('id'))
                
                if convert_data.exists():
                    labels = []
                    data = []
                    for item in convert_data:
                        status = 'Converted' if item[convert_field] else 'Not Converted'
                        labels.append(status)
                        data.append(item['count'])
                    
                    return {
                        'title': 'Lead Conversion Status',
                        'type': 'column',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': 'Status'
                        }
                    }
            
            if hasattr(queryset.model, 'status'):
                status_data = queryset.values('status').annotate(count=Count('id')).order_by('-count')
                
                if status_data.exists():
                    labels = [item['status'] or 'No Status' for item in status_data]
                    data = [item['count'] for item in status_data]
                    
                    return {
                        'title': 'Leads by Status',
                        'type': 'funnel',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': 'Status'
                        }
                    }
            
        except Exception as e:
            logger.warning(f"Error creating lead chart: {e}")
        
        return None
    

    def create_opportunity_charts(self, queryset, model_info):
        """Create opportunity-specific charts"""
        try:
            if hasattr(queryset.model, 'lead_source') or hasattr(queryset.model, 'source'):
                source_field = 'lead_source' if hasattr(queryset.model, 'lead_source') else 'source'
                source_data = queryset.values(source_field).annotate(count=Count('id')).order_by('-count')
                
                if source_data.exists():
                    labels = [item[source_field] or 'Unknown' for item in source_data]
                    data = [item['count'] for item in source_data]
                    
                    return {
                        'title': 'Opportunities by Lead Source',
                        'type': 'column',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': 'Lead Source'
                        }
                    }
            
            stage_field = None
            if hasattr(queryset.model, 'stage'):
                stage_field = 'stage'
            elif hasattr(queryset.model, 'status'):
                stage_field = 'status'
            elif hasattr(queryset.model, 'opportunity_stage'):
                stage_field = 'opportunity_stage'
            
            if stage_field:
                stage_data = queryset.values(stage_field).annotate(count=Count('id')).order_by('-count')
                
                if stage_data.exists():
                    labels = [item[stage_field] or 'Unknown' for item in stage_data]
                    data = [item['count'] for item in stage_data]
                    
                    return {
                        'title': 'Opportunities by Stage',
                        'type': 'funnel',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': 'Stage'
                        }
                    }
            
            if hasattr(queryset.model, 'is_won'):
                won_data = queryset.values('is_won').annotate(count=Count('id'))
                
                if won_data.exists():
                    labels = []
                    data = []
                    for item in won_data:
                        status = 'Won' if item['is_won'] else 'In Progress/Lost'
                        labels.append(status)
                        data.append(item['count'])
                    
                    return {
                        'title': 'Opportunity Win Rate',
                        'type': 'pie',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': 'Status'
                        }
                    }
            
            if hasattr(queryset.model, 'amount') or hasattr(queryset.model, 'value'):
                amount_field = 'amount' if hasattr(queryset.model, 'amount') else 'value'
                
                opportunities = list(queryset.values('id', amount_field).exclude(**{f'{amount_field}__isnull': True}))
                if opportunities:
                    ranges = ['<10K', '10K-50K', '50K-100K', '100K+']
                    range_counts = [0, 0, 0, 0]
                    
                    for opp in opportunities:
                        amount = float(opp[amount_field] or 0)
                        if amount < 10000:
                            range_counts[0] += 1
                        elif amount < 50000:
                            range_counts[1] += 1
                        elif amount < 100000:
                            range_counts[2] += 1
                        else:
                            range_counts[3] += 1
                    
                    return {
                        'title': 'Opportunities by Value Range',
                        'type': 'column',
                        'data': {
                            'labels': ranges,
                            'data': range_counts,
                            'labelField': 'Value Range'
                        }
                    }
                    
        except Exception as e:
            logger.warning(f"Error creating opportunity chart: {e}")
        
        return None


    def create_campaign_charts(self, queryset, model_info):
        """Create campaign-specific charts"""
        try:
            if hasattr(queryset.model, 'campaign_type') or hasattr(queryset.model, 'type'):
                type_field = 'campaign_type' if hasattr(queryset.model, 'campaign_type') else 'type'
                type_data = queryset.values(type_field).annotate(count=Count('id')).order_by('-count')
                
                if type_data.exists():
                    labels = [item[type_field] or 'Unknown' for item in type_data]
                    data = [item['count'] for item in type_data]
                    
                    return {
                        'title': 'Campaigns by Type',
                        'type': 'donut',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': 'Campaign Type'
                        }
                    }
            
            if hasattr(queryset.model, 'status'):
                status_data = queryset.values('status').annotate(count=Count('id')).order_by('-count')
                
                if status_data.exists():
                    labels = [item['status'] or 'No Status' for item in status_data]
                    data = [item['count'] for item in status_data]
                    
                    return {
                        'title': 'Campaigns by Status',
                        'type': 'column',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': 'Status'
                        }
                    }
            
            if hasattr(queryset.model, 'is_active'):
                active_data = queryset.values('is_active').annotate(count=Count('id'))
                
                if active_data.exists():
                    labels = []
                    data = []
                    for item in active_data:
                        status = 'Active' if item['is_active'] else 'Inactive'
                        labels.append(status)
                        data.append(item['count'])
                    
                    return {
                        'title': 'Campaign Activity Status',
                        'type': 'column',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': 'Activity'
                        }
                    }
                    
        except Exception as e:
            logger.warning(f"Error creating campaign chart: {e}")
        
        return None
    

    def create_contact_charts(self, queryset, model_info):
        """Create contact-specific charts"""
        try:
            if hasattr(queryset.model, 'lead_source') or hasattr(queryset.model, 'source'):
                source_field = 'lead_source' if hasattr(queryset.model, 'lead_source') else 'source'
                source_data = queryset.values(source_field).annotate(count=Count('id')).order_by('-count')
                
                if source_data.exists():
                    labels = [item[source_field] or 'Unknown' for item in source_data]
                    data = [item['count'] for item in source_data]
                    
                    return {
                        'title': 'Contacts by Source',
                        'type': 'pie',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': 'Source'
                        }
                    }
            
            category_field = None
            if hasattr(queryset.model, 'contact_type'):
                category_field = 'contact_type'
            elif hasattr(queryset.model, 'category'):
                category_field = 'category'
            elif hasattr(queryset.model, 'type'):
                category_field = 'type'
            
            if category_field:
                cat_data = queryset.values(category_field).annotate(count=Count('id')).order_by('-count')
                
                if cat_data.exists():
                    labels = [item[category_field] or 'Uncategorized' for item in cat_data]
                    data = [item['count'] for item in cat_data]
                    
                    return {
                        'title': f'Contacts by {category_field.replace("_", " ").title()}',
                        'type': 'column',
                        'data': {
                            'labels': labels,
                            'data': data,
                            'labelField': category_field.replace("_", " ").title()
                        }
                    }
            
        except Exception as e:
            logger.warning(f"Error creating contact chart: {e}")
        
        return None
    

    def create_generic_chart(self, queryset, model_info):
        """Create generic chart for other models"""
        try:
            for field in queryset.model._meta.fields:
                if hasattr(field, 'choices') and field.choices:
                    choice_data = queryset.values(field.name).annotate(count=Count('id')).order_by('-count')
                    
                    if choice_data.exists():
                        labels = []
                        data = []
                        
                        for item in choice_data:
                            value = item[field.name]
                            display_value = value
                            
                            for choice_value, choice_label in field.choices:
                                if choice_value == value:
                                    display_value = choice_label
                                    break
                            
                            labels.append(str(display_value) if display_value is not None else 'None')
                            data.append(item['count'])
                        
                        return {
                            'title': f"{model_info['name']} by {field.verbose_name}",
                            'type': 'pie',
                            'data': {
                                'labels': labels,
                                'data': data,
                                'labelField': field.verbose_name
                            }
                        }
            
            date_field = self.get_date_field(queryset.model)
            if date_field:
                return self.create_time_chart(queryset, model_info, date_field)
                
        except Exception as e:
            logger.warning(f"Error creating generic chart: {e}")
        
        return None
    

    def generate_table_data(self):
        tables = []

        lead_model = next((m for m in self.models if m['model'].__name__.lower() == 'lead'), None)

       

        if lead_model:
            app_label = lead_model['model']._meta.app_label
            model_name = lead_model['model']._meta.model_name
            permission = f"{app_label}.view_{model_name}"

            table = self.build_table_context(
                model_info=lead_model,
                title="Won Leads",
                filter_kwargs={"lead_status__name__icontains": "Won"} if hasattr(lead_model['model'], "lead_status") else {},
                no_record_msg="No won leads found.",
                view_id="leads_dashboard_list"
            )
            if self.user.has_perm(permission):
                if table:
                    tables.append(table)

        opp_model = next((m for m in self.models if m['model'].__name__.lower() == 'opportunity'), None)
        if opp_model:
            app_label = opp_model['model']._meta.app_label
            model_name = opp_model['model']._meta.model_name
            permission = f"{app_label}.view_{model_name}"
            
            table = self.build_table_context(
                model_info=opp_model,
                title="Closed Won Opportunities",
                filter_kwargs={"stage__name": "Closed Won"} if hasattr(opp_model['model'], "stage") else {},
                no_record_msg="No closed won opportunities found.",
                view_id="opportunities_dashboard_list"
            )
            if self.user.has_perm(permission):
                if table:
                    tables.append(table)

        return tables


    def build_table_context(self, model_info, title, filter_kwargs, no_record_msg, view_id, request=None):
        """
        Build table context with pagination for infinite scroll
        """
        try:
            request = getattr(_thread_local, "request", None)
            qs = self.get_queryset(model_info['model'])
            if filter_kwargs:
                qs = qs.filter(**filter_kwargs)

            sort_field = request.GET.get('sort', None) if request else None
            sort_direction = request.GET.get('direction', 'asc') if request else 'asc'
            if sort_field:
                prefix = '-' if sort_direction == 'desc' else ''
                try:
                    qs = qs.order_by(f"{prefix}{sort_field}")
                except:
                    qs = qs.order_by('id')
            else:
                date_field = self.get_date_field(model_info['model'])
                order_field = f"-{date_field}" if date_field else "-pk"
                qs = qs.order_by(order_field)

            page = request.GET.get('page', 1) if request else 1
            paginator = Paginator(qs, 10)  
            try:
                page_obj = paginator.get_page(page)
            except:
                page_obj = paginator.get_page(1)

            has_next = page_obj.has_next()
            next_page = page_obj.next_page_number() if has_next else None

            table_fields = self.get_model_specific_table_fields(model_info)
            if not table_fields:
                return None

            columns = [(f["verbose_name"], f["name"]) for f in table_fields]
            filtered_ids = list(qs.values_list("id", flat=True))

            return {
                "id": f"table_{model_info['model']._meta.model_name}_{uuid.uuid4().hex[:8]}",
                "title": title,
                "queryset": page_obj.object_list,
                "columns": columns,
                "view_id": view_id,
                "model_name": model_info["model"]._meta.model_name,
                "model_verbose_name": model_info["model"]._meta.verbose_name_plural,
                "total_records_count": qs.count(),
                "bulk_select_option": False,
                "bulk_export_option": False,
                "bulk_update_option": False,
                "bulk_delete_enabled": False,
                "clear_session_button_enabled": False,
                "enable_sorting": True,
                "visible_actions": [],
                "action_method": None,
                "additional_action_button": [],
                "custom_bulk_actions": [],
                "search_url": "",
                "search_params": request.GET.urlencode() if request else "",
                "filter_fields": [],
                "filter_set_class": None,
                "table_class": True,
                "table_width": False,
                "table_height": False,
                "table_height_as_class": "h-[300px]",
                "header_attrs": {},
                "col_attrs": {},
                "selected_ids": filtered_ids,
                "selected_ids_json": json.dumps(filtered_ids),
                "current_sort": sort_field if request else "",
                "current_direction": sort_direction if request else "",
                "main_url": "",
                "view_type": "dashboard",
                "no_record_msg": no_record_msg,
                "no_record_add_button": {},
                "page_obj": page_obj,
                "has_next": has_next,
                "next_page": next_page,
            }
        except Exception as e:
            logger.warning(f"Failed to generate table for {model_info['name']}: {e}")
            return None
    

    def get_model_specific_table_fields(self, model_info):
            model_name = model_info['model'].__name__.lower()
            model_class = model_info['model']
            
            if model_name == 'lead':
                return self.get_lead_table_fields(model_class)
            elif model_name == 'contact':
                return self.get_contact_table_fields(model_class)
            elif model_name == 'opportunity':
                return self.get_opportunity_table_fields(model_class)
            elif model_name == 'campaign':
                return self.get_campaign_table_fields(model_class)
            elif model_name == 'account':
                return self.get_account_table_fields(model_class)
            else:
                return self.get_table_fields(model_class)
            

    def get_lead_table_fields(self, model_class):
        priority_fields = ['first_name', 'last_name', 'email', 'company', 'lead_source']
        return self.get_priority_fields(model_class, priority_fields, max_fields=5)
    

    def get_opportunity_table_fields(self, model_class):
        priority_fields = ['name', 'title', 'account', 'amount', 'stage']
        return self.get_priority_fields(model_class, priority_fields, max_fields=5)
    

    def get_priority_fields(self, model_class, priority_fields, max_fields=5):
        suitable_fields = []
        excluded_fields = ['id', 'password', 'updated_at']
        
        for field_name in priority_fields:
            if len(suitable_fields) >= max_fields:
                break
                
            try:
                field = model_class._meta.get_field(field_name)
                if (field_name not in excluded_fields and 
                    not field_name.endswith('_id') and
                    field.get_internal_type() in [
                        'CharField', 'TextField', 'IntegerField', 'FloatField', 
                        'DecimalField', 'BooleanField', 'DateField', 'DateTimeField', 
                        'EmailField', 'ForeignKey'
                    ]):
                    
                    suitable_fields.append({
                        'name': field.name,
                        'verbose_name': field.verbose_name or field.name.replace('_', ' ').title()
                    })
            except:
                continue
        
        if len(suitable_fields) < max_fields:
            for field in model_class._meta.fields:
                if len(suitable_fields) >= max_fields:
                    break
                    
                if (field.name not in excluded_fields and 
                    not field.name.endswith('_id') and
                    field.name not in [f['name'] for f in suitable_fields] and
                    field.get_internal_type() in [
                        'CharField', 'TextField', 'IntegerField', 'FloatField', 
                        'DecimalField', 'BooleanField', 'DateField', 'DateTimeField', 'EmailField'
                    ]):
                    
                    suitable_fields.append({
                        'name': field.name,
                        'verbose_name': field.verbose_name or field.name.replace('_', ' ').title()
                    })
        
        return suitable_fields
    

    def get_table_fields(self, model_class):
        suitable_fields = []
        excluded_fields = ['id', 'password', 'created_at', 'updated_at']
        
        for field in model_class._meta.fields[:6]:
            if (field.name not in excluded_fields and 
                not field.name.endswith('_id') and
                field.get_internal_type() in [
                    'CharField', 'TextField', 'IntegerField', 'FloatField', 
                    'DecimalField', 'BooleanField', 'DateField', 'DateTimeField', 'EmailField'
                ]):
                
                suitable_fields.append({
                    'name': field.name,
                    'verbose_name': field.verbose_name or field.name.replace('_', ' ').title()
                })
                
                if len(suitable_fields) >= 4:
                    break
        
        return suitable_fields
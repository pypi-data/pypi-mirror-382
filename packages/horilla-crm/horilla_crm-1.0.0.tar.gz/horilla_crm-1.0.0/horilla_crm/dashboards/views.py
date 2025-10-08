from urllib.parse import urlencode
from django.apps import apps
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, render  # type: ignore
from django.utils.functional import cached_property  # type: ignore
from django.urls import reverse_lazy
from horilla_crm.dashboards.filters import DashboardFilter
from horilla_crm.dashboards.forms import DashboardCreateForm
from horilla_crm.dashboards.models import Dashboard, DashboardComponent,ComponentCriteria, DashboardFolder
from django.utils.translation import gettext_lazy as _
from horilla_generics.mixins import RecentlyViewedMixin
from horilla_generics.views import (
    HorillaNavView,
    HorillaListView,
    HorillaSingleDeleteView,
    HorillaSingleFormView,
    
)
from .utils import DefaultDashboardGenerator
from django.contrib import messages
from horilla_utils.middlewares import _thread_local
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.utils import timezone
from django.views.generic import TemplateView
from django.template.loader import render_to_string
import json
from django.db import transaction
from django.db.models import Count, Sum, Avg, Max, Min
from django.db.models import ForeignKey
from django.core.paginator import Paginator
import logging
logger = logging.getLogger(__name__)
from django.utils.decorators import method_decorator
from horilla_core.decorators import htmx_required, permission_required_or_denied,permission_required
from django.db.models import Q



class HomePageView(LoginRequiredMixin, TemplateView):
    
    template_name = "home/default_home.html"
    
    def get(self, request, *args, **kwargs):
        try:
            default_dashboard = Dashboard.get_default_dashboard(request.user)
            
            if default_dashboard:
                return self.render_dashboard_as_home(request, default_dashboard)
        except ImportError:
            logger.warning("Dashboard model not found")
        
        return self.render_dynamic_default_dashboard(request)
    
    def render_dashboard_as_home(self, request, dashboard):
        try:
            
            detail_view = DashboardDetailView()
            detail_view.request = request
            detail_view.object = dashboard
            detail_view.kwargs = {'pk': dashboard.pk}
            
            mutable_get = request.GET.copy()
            mutable_get['section'] = 'home'
            mutable_get['is_home'] = 'true'
            request.GET = mutable_get
            
            context = detail_view.get_context_data(object=dashboard)
            template_name = detail_view.get_template_names()[0]
            
            return self.render_to_response(context, template_name=template_name)
        except ImportError:
            return self.render_dynamic_default_dashboard(request)
    
    def render_dynamic_default_dashboard(self, request):
        context = self.get_dynamic_default_context()
        return self.render_to_response(context, template_name="home/default_home.html")
    
    def get_dynamic_default_context(self):
        context = super().get_context_data()
        
        user_company = getattr(self.request.user, 'company', None)
        
        generator = DefaultDashboardGenerator(self.request.user, user_company)
        
        kpi_data = generator.generate_kpi_data()
        chart_data = generator.generate_chart_data()
        table_data = generator.generate_table_data()
        
        user_dashboards = []
        try:
            user_dashboards = Dashboard.objects.filter(
                dashboard_owner=self.request.user,
                is_active=True
            ).order_by('-created_at')[:5]
        except ImportError:
            pass
        
        context.update({
            'is_default_home': True,
            'is_dynamic_dashboard': True,
            'kpi_data': kpi_data,
            'chart_data': chart_data,
            'table_data': table_data,
            'user_dashboards': user_dashboards,
            'has_dashboards': bool(user_dashboards),
            'show_create_dashboard_prompt': True,
            'available_models_count': len(generator.models),
        })
        
        return context
    
    def render_to_response(self, context, template_name=None, **response_kwargs):
        if template_name:
            self.template_name = template_name
        return super().render_to_response(context, **response_kwargs) 


def get_queryset_for_module(user, model):
    """
    Returns queryset for a given model based on user permissions.
    Uses model.OWNER_FIELDS if available.
    """
    app_label = model._meta.app_label
    model_name = model._meta.model_name

    if user.has_perm(f"{app_label}.view_{model_name}"):
        return model.objects.all()

    elif user.has_perm(f"{app_label}.view_own_{model_name}"):
        owner_fields = getattr(model, "OWNER_FIELDS", [])
        if not owner_fields:
            return model.objects.none()

        q_filter = Q()
        for field in owner_fields:
            q_filter |= Q(**{field: user})
        return model.objects.filter(q_filter)

    return model.objects.none()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard_view.html"


@method_decorator(permission_required(["dashboards.view_dashboard","dashboards.view_own_dashboard"]), name="dispatch")
class DashboardNavbar(LoginRequiredMixin, HorillaNavView):
    search_url = reverse_lazy("dashboards:dashboard_list_view")
    main_url = reverse_lazy("dashboards:dashboard_list_view")
    filterset_class = DashboardFilter
    list_view_only = True
    filter_option = False
    reload_option = False
    gap_enabled = False
    model_name = "Dashboard"
    model_app_label = "dashboards"
    search_option = False
    all_view_types = False


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.request.GET.get('title', 'Dashboards')
        context['nav_title'] = title
        return context

    @cached_property
    def new_button(self):
        if self.request.user.has_perm("dashboards.add_dashboard"):
            return {
                "title": "New Dashboard",
                "url": f"""{ reverse_lazy('dashboards:dashboard_create')}""",
                "attrs": {"id": "dashboard-create"},
            }

    @cached_property
    def second_button(self):
        if self.request.user.has_perm("dashboards.add_dashboardfolder"):
            return {
                "title": "New Folder",
                "url": f"{reverse_lazy('dashboards:dashboard_folder_create')}?pk={self.request.GET.get('pk', '')}",
                "attrs": {"id": "dashboard-folder-create"},
            }
    

@method_decorator(permission_required_or_denied(["dashboards.view_dashboard","dashboards.view_own_dashboard"]), name="dispatch")
class DashboardListView(LoginRequiredMixin, HorillaListView):
    model = Dashboard
    template_name = "dashboard_list_view.html"
    view_id = "dashboard-list"
    search_url = reverse_lazy("dashboards:dashboard_list_view")
    main_url = reverse_lazy("dashboards:dashboard_list_view")
    table_width = False
    max_visible_actions = 5
    bulk_select_option = False
    sorting_target = f"#tableview-{view_id}"
    # enable_sorting =  False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Dashboards"
        return context

    @cached_property
    def columns(self):
        instance = self.model()
        return [
            (instance._meta.get_field("name").verbose_name, "name"),
            (instance._meta.get_field("description").verbose_name, "description"),
            (instance._meta.get_field("folder").verbose_name, "folder"),
            (instance._meta.get_field("is_default").verbose_name, "is_default"),
        ]
    @cached_property
    def action_method(self):
        action_method = ""
        if self.request.user.has_perm("dashboards.change_dashboard") or self.request.user.has_perm("dashboards.delete_dashboard") or self.request.user.has_perm("dashboards.view_own_dashboard"):
            action_method = "actions"
        return action_method


    @cached_property
    def col_attrs(self):
        query_params = {}
        if "section" in self.request.GET:
            query_params["section"] = self.request.GET.get("section")
        query_string = urlencode(query_params)
        attrs = {}
        if self.request.user.has_perm("dashboards.view_dashboard") or self.request.user.has_perm("dashboards.view_own_dashboard"):
            attrs = {
                "hx-get": f"{{get_detail_view_url}}?{query_string}",
                "hx-target": "#mainContent",
                "hx-swap": "outerHTML",
                "hx-push-url": "true",
                "hx-select": "#mainContent",
                "style": "cursor:pointer",
                "class": "hover:text-primary-600",
            }
        return [
            {
                "name": {
                    **attrs,
                }
            }
        ]


class DashboardFavoriteToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            dashboard = Dashboard.objects.get(pk=kwargs['pk'])
            user = request.user
            if user.is_superuser or user.has_perm("dashboards.change_dashboard") or dashboard.dashboard_owner == user:
                if user in dashboard.favourited_by.all():
                    dashboard.favourited_by.remove(user)
                    messages.success(request, f"Removed {dashboard.name} from favorites.")
                else:
                    dashboard.favourited_by.add(user)
                    messages.success(request, f"Added {dashboard.name} to favorites.")
                return HttpResponse(headers={"HX-Refresh": "true"})
            else:
                return render(request, "403.html")
        except Dashboard.DoesNotExist:
            return HttpResponse("<script>alert('Dashboard not found');</script>", status=404)
        except Exception as e:
            return HttpResponse(f"<script>alert('Error: {str(e)}');</script>", status=500)

    def get(self,request, *args, **kwargs):
        return render(request, "403.html")
        

@method_decorator(permission_required_or_denied(["dashboards.view_dashboard","dashboards.view_own_dashboard"]), name="dispatch")
class DashboardDetailView(RecentlyViewedMixin,LoginRequiredMixin, TemplateView):
    """
    Render the detail view of dashboard page.
    """
    model = Dashboard

    def get_template_names(self):
        """
        Return template based on whether this is accessed from home
        """
        section = self.request.GET.get('section')
        is_home = self.request.GET.get('is_home') == 'true'
        is_default = self.object.is_default if hasattr(self, 'object') and self.object else False
        
        if section == 'home' and is_home and is_default:
            return ['home/home.html']
        else:
            return ['dashboard_detail_view.html'] 

    def get_object(self):
        if not hasattr(self, '_object'):
            self._object = get_object_or_404(self.model, pk=self.kwargs.get("pk"))
        return self._object
    
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.model.objects.filter(dashboard_owner_id=self.request.user,pk=self.kwargs["pk"]).first() and not self.request.user.has_perm("dashboards.view_dashboard"):
            return render(self.request,"403.html")
        return super().get(request, *args, **kwargs)


    def get_table_data(self, component, request):
        """
        Generate table data and context for a dashboard component using HorillaListView.
        Adapted from DashboardComponentTableView.get_table_data.
        """
        model = None
        for app_config in apps.get_app_configs():
            try:
                model = apps.get_model(app_label=app_config.label, model_name=component.module.lower())
                break
            except LookupError:
                continue
        
        if not model:
            return None, {}

        queryset = get_queryset_for_module(self.request.user, model)
        conditions = component.conditions.all().order_by('sequence')
        for condition in conditions:
            field = condition.field
            operator = condition.operator
            value = condition.value
            if operator == 'equals':
                queryset = queryset.filter(**{f"{field}": value})
            elif operator == 'not_equals':
                queryset = queryset.exclude(**{f"{field}": value})
            elif operator == 'greater_than':
                try:
                    queryset = queryset.filter(**{f"{field}__gt": float(value)})
                except ValueError:
                    queryset = queryset.filter(**{f"{field}__gt": value})
            elif operator == 'less_than':
                try:
                    queryset = queryset.filter(**{f"{field}__lt": float(value)})
                except ValueError:
                    queryset = queryset.filter(**{f"{field}__lt": value})
            elif operator == 'greater_equal':
                try:
                    queryset = queryset.filter(**{f"{field}__gte": float(value)})
                except ValueError:
                    queryset = queryset.filter(**{f"{field}__gte": value})
            elif operator == 'less_equal':
                try:
                    queryset = queryset.filter(**{f"{field}__lte": float(value)})
                except ValueError:
                    queryset = queryset.filter(**{f"{field}__lte": value})
            elif operator == 'contains':
                queryset = queryset.filter(**{f"{field}__icontains": value})
            elif operator == 'not_contains':
                queryset = queryset.exclude(**{f"{field}__icontains": value})
            elif operator == 'starts_with':
                queryset = queryset.filter(**{f"{field}__istartswith": value})
            elif operator == 'ends_with':
                queryset = queryset.filter(**{f"{field}__iendswith": value})
            elif operator == 'is_null':
                queryset = queryset.filter(**{f"{field}__isnull": True})
            elif operator == 'is_not_null':
                queryset = queryset.filter(**{f"{field}__isnull": False})

        sort_field = request.GET.get('sort', None)
        sort_direction = request.GET.get('direction', 'asc')
        if sort_field:
            prefix = '-' if sort_direction == 'desc' else ''
            try:
                queryset = queryset.order_by(f"{prefix}{sort_field}")
            except:
                queryset = queryset.order_by('id')
        else:
            queryset = queryset.order_by('id')
       

        paginator = Paginator(queryset, 10) 
        page = request.GET.get('page', 1)
        page_obj = paginator.get_page(page)
        has_next = page_obj.has_next()
        next_page = page_obj.next_page_number() if has_next else None

        columns = []
        if component.columns:
            try:
                if isinstance(component.columns, str):
                    if component.columns.startswith('['):
                        selected_columns = json.loads(component.columns)
                    else:
                        selected_columns = [col.strip() for col in component.columns.split(',') if col.strip()]
                else:
                    selected_columns = component.columns
            except:
                selected_columns = []
        else:
            selected_columns = []
            for field in model._meta.get_fields()[:5]:
                if field.concrete and not field.is_relation:
                    selected_columns.append(field.name)

        for column in selected_columns:
            try:
                field = model._meta.get_field(column)
                verbose_name = field.verbose_name or column.replace('_', ' ').title()
                if hasattr(field, 'choices') and field.choices:
                    columns.append((verbose_name, f'get_{column}_display'))
                else:
                    columns.append((verbose_name, column))
            except:
                continue

        if not columns:
            for field in model._meta.get_fields()[:3]:
                if field.concrete and not field.is_relation:
                    columns.append((field.verbose_name or field.name.replace('_', ' ').title(), field.name))

        query_params = request.GET.urlencode()

        table_data_url = reverse_lazy('dashboards:component_table_data', kwargs={'component_id': component.id})

        list_view = HorillaListView(
            model=model,
            view_id=f"dashboard_component_{component.id}",
            search_url=table_data_url,  
            main_url=reverse_lazy('dashboards:dashboard_detail_view', kwargs={'pk': component.dashboard_id}),
            table_width=False,
            filterset_class=getattr(model, 'FilterSet', None),
            columns=columns,
        )
        list_view.request = request
        list_view.table_width = False
        list_view.bulk_select_option = True
        list_view.bulk_export_option = True
        list_view.bulk_update_option = False
        list_view.bulk_delete_enabled = False
        list_view.clear_session_button_enabled = True
        list_view.list_column_visibility = False
        list_view.table_height = False
        list_view.table_height_as_class = "h-[300px]"
        list_view.object_list = page_obj.object_list
        list_view.enable_sorting = True
        list_view.has_next = has_next
        list_view.next_page = next_page
        list_view.search_params = query_params
        list_view.model_verbose_name = model._meta.verbose_name_plural
        list_view.total_records_count = queryset.count()
        list_view.selected_ids_json = json.dumps([])
        list_view.list_column_visibility = False

        filtered_ids = list(queryset.values_list("id", flat=True))
        list_view.selected_ids_json = json.dumps(filtered_ids)

        context = list_view.get_context_data(object_list=page_obj.object_list)

        context.update({
            'no_record_msg': f"No {model._meta.verbose_name_plural} found matching the specified criteria.",
            'header_attrs': {},
            'col_attrs': {},
            'visible_actions': [],  
            'custom_bulk_actions': [],
            'additional_action_button': [],
            'filter_set_class': None,  
            'filter_fields': list_view._get_model_fields(),
            'total_records_count': queryset.count(),
            'selected_ids': filtered_ids,  
            'selected_ids_json': json.dumps(filtered_ids), 
            'queryset': page_obj.object_list, 
            'page_obj': page_obj,
            'search_url': table_data_url,  
            'search_params': query_params,
            'has_next': has_next,
            'next_page': next_page,
            'component': component,
            'view_id': f"dashboard_component_{component.id}",
            'app_label': model._meta.app_label,
            'model_name': model._meta.model_name,
            'model_verbose_name': model._meta.verbose_name_plural,
        })

        return model, context


    def post(self, request, *args, **kwargs):
        dashboard = self.get_object()
        components = DashboardComponent.objects.filter(
            dashboard=dashboard,
            is_active=True,
            component_type='table_data'
        ).order_by('sequence')

        for component in components:
            model, table_context = self.get_table_data(component, request)
            if model:
                list_view = HorillaListView(
                    view_id=f"dashboard_component_{component.id}",
                    model=model,
                    request=request,
                    search_url=f"{reverse_lazy('dashboards:dashboard_detail_view', kwargs={'pk': component.dashboard_id})}",
                    main_url=reverse_lazy('dashboards:dashboard_detail_view', kwargs={'pk': component.dashboard_id}),
                    columns=table_context.get('columns', []),
                    bulk_export_option=True
                )
                list_view.object_list = table_context.get('queryset', model.objects.all())
                return list_view.post(request, *args, **kwargs)

        return HttpResponse("No table component found to handle export", status=400)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        section = self.request.GET.get('section')
        is_home = self.request.GET.get('is_home') == 'true'
        is_default = self.object.is_default
        is_home_view = section == 'home' and is_home and is_default

        dashboard = self.get_object()
        components = DashboardComponent.objects.filter(
            dashboard=dashboard,
            is_active=True
        ).order_by('sequence')

        table_contexts = {}
        for component in components.filter(component_type='table_data'):
            model, table_context = self.get_table_data(component, self.request)
            if model:
                table_contexts[component.id] = table_context
        

        context.update({
            "current_obj": dashboard,
            "dashboard": dashboard,
            "components": components,
            "has_components": components.exists(),
            "table_contexts": table_contexts,
            "view_id": "dashboard_components",
            'is_home_view': is_home_view,
            'section': section,
            'is_home': is_home,
        })
        
        return context  
  

@method_decorator(permission_required_or_denied(["dashboards.view_dashboard","dashboards.view_own_dashboard"]), name="dispatch")
class DashboardComponentTableDataView(LoginRequiredMixin, View):
    """
    Handle AJAX requests for table data pagination and search
    """
     
    
    def get(self, request, *args, **kwargs):
        component_id = kwargs.get('component_id')
        
        try:
            component = DashboardComponent.objects.get(
                id=component_id,
                component_type='table_data',
                is_active=True
            )
        except DashboardComponent.DoesNotExist:
            return HttpResponse("Component not found", status=404)
        
        # Get model
        model = None
        for app_config in apps.get_app_configs():
            try:
                model = apps.get_model(app_label=app_config.label, model_name=component.module.lower())
                break
            except LookupError:
                continue
        
        if not model:
            return HttpResponse("Model not found", status=404)

        # Build queryset
        queryset = model.objects.all()
        
        # Apply conditions
        conditions = component.conditions.all().order_by('sequence')
        for condition in conditions:
            field = condition.field
            operator = condition.operator
            value = condition.value
            if operator == 'equals':
                queryset = queryset.filter(**{f"{field}": value})
            elif operator == 'not_equals':
                queryset = queryset.exclude(**{f"{field}": value})
            elif operator == 'greater_than':
                try:
                    queryset = queryset.filter(**{f"{field}__gt": float(value)})
                except ValueError:
                    queryset = queryset.filter(**{f"{field}__gt": value})
            elif operator == 'less_than':
                try:
                    queryset = queryset.filter(**{f"{field}__lt": float(value)})
                except ValueError:
                    queryset = queryset.filter(**{f"{field}__lt": value})
            elif operator == 'greater_equal':
                try:
                    queryset = queryset.filter(**{f"{field}__gte": float(value)})
                except ValueError:
                    queryset = queryset.filter(**{f"{field}__gte": value})
            elif operator == 'less_equal':
                try:
                    queryset = queryset.filter(**{f"{field}__lte": float(value)})
                except ValueError:
                    queryset = queryset.filter(**{f"{field}__lte": value})
            elif operator == 'contains':
                queryset = queryset.filter(**{f"{field}__icontains": value})
            elif operator == 'not_contains':
                queryset = queryset.exclude(**{f"{field}__icontains": value})
            elif operator == 'starts_with':
                queryset = queryset.filter(**{f"{field}__istartswith": value})
            elif operator == 'ends_with':
                queryset = queryset.filter(**{f"{field}__iendswith": value})
            elif operator == 'is_null':
                queryset = queryset.filter(**{f"{field}__isnull": True})
            elif operator == 'is_not_null':
                queryset = queryset.filter(**{f"{field}__isnull": False})

        # Apply sorting
        sort_field = request.GET.get('sort', None)
        sort_direction = request.GET.get('direction', 'asc')
        if sort_field:
            prefix = '-' if sort_direction == 'desc' else ''
            try:
                queryset = queryset.order_by(f"{prefix}{sort_field}")
            except:
                queryset = queryset.order_by('id')
        else:
            queryset = queryset.order_by('id')

        total_count = queryset.count()
        
        if total_count == 0:
            if request.headers.get('HX-Request'):
                return HttpResponse("")
            else:
                return HttpResponse("No data available")

        # Pagination
        paginator = Paginator(queryset, 10)
        page = request.GET.get('page', 1)
        
        try:
            page_obj = paginator.get_page(page)
        except Exception as e:
            if request.headers.get('HX-Request'):
                return HttpResponse("")
            return HttpResponse("Invalid page")
        
        has_next = page_obj.has_next()
        next_page = page_obj.next_page_number() if has_next else None

        # Build columns
        columns = []
        if component.columns:
            try:
                if isinstance(component.columns, str):
                    if component.columns.startswith('['):
                        selected_columns = json.loads(component.columns)
                    else:
                        selected_columns = [col.strip() for col in component.columns.split(',') if col.strip()]
                else:
                    selected_columns = component.columns
            except:
                selected_columns = []
        else:
            selected_columns = []
            for field in model._meta.get_fields()[:5]:
                if field.concrete and not field.is_relation:
                    selected_columns.append(field.name)

        for column in selected_columns:
            try:
                field = model._meta.get_field(column)
                verbose_name = field.verbose_name or column.replace('_', ' ').title()
                if hasattr(field, 'choices') and field.choices:
                    columns.append((verbose_name, f'get_{column}_display'))
                else:
                    columns.append((verbose_name, column))
            except:
                continue

        if not columns:
            for field in model._meta.get_fields()[:3]:
                if field.concrete and not field.is_relation:
                    columns.append((field.verbose_name or field.name.replace('_', ' ').title(), field.name))

        query_params = self.request.GET.urlencode()
        
        table_data_url = reverse_lazy('dashboards:component_table_data', kwargs={'component_id': component.id})

        # Create the full table_context similar to DashboardDetailView
        filtered_ids = list(queryset.values_list("id", flat=True))
        
        table_context = {
            'queryset': page_obj.object_list,
            'columns': columns,
            'search_url': table_data_url,
            'search_params': query_params,
            'has_next': has_next,
            'next_page': next_page,
            'page_obj': page_obj,
            'bulk_select_option': True,
            'visible_actions': [],
            'col_attrs': {},
            'table_class': True,
            'no_record_msg': f"No {model._meta.verbose_name_plural} found matching the specified criteria.",
            'header_attrs': {},
            'visible_actions': [],  
            'custom_bulk_actions': [],
            'additional_action_button': [],
            'filter_set_class': None,  
            'filter_fields': [],  # You might need to populate this if needed
            'total_records_count': total_count,
            'selected_ids': filtered_ids,  
            'selected_ids_json': json.dumps(filtered_ids), 
            'component': component,
            'model_verbose_name': model._meta.verbose_name_plural,
            'view_id': f"dashboard_component_{component.id}",
            'app_label': model._meta.app_label,
            'model_name': model._meta.model_name,
        }

        if request.headers.get('HX-Request'):
            return render(request, 'list_view.html', table_context)
        
        context = {
            'current_obj': component.dashboard,
            'dashboard': component.dashboard,
            'components': DashboardComponent.objects.filter(dashboard=component.dashboard, is_active=True),
            'has_components': True,
            '': 100, 
            'table_contexts': {component.id: table_context},
        }
        
        return render(request, 'list_view.html', context)

    def post(self, request, *args, **kwargs):
        """Handle bulk operations"""
        component_id = kwargs.get('component_id')
        
        try:
            component = DashboardComponent.objects.get(
                id=component_id,
                component_type='table_data',
                is_active=True
            )
        except DashboardComponent.DoesNotExist:
            return HttpResponse("Component not found", status=404)
        
        dashboard_view = DashboardDetailView()
        model, table_context = dashboard_view.get_table_data(component, request)
        
        if model:
            list_view = HorillaListView(
                model=model,
                request=request,
                view_id=f"table_{component.id}",
                search_url=reverse_lazy('dashboards:component_table_data', kwargs={'component_id': component.id}),
                main_url=reverse_lazy('dashboards:dashboard_detail_view', kwargs={'pk': component.dashboard_id}),
                columns=table_context.get('columns', []),
                bulk_export_option=True
            )
            list_view.object_list = table_context.get('queryset', model.objects.all())
            return list_view.post(request, *args, **kwargs)
        
        return HttpResponse("No table component found to handle export", status=400)


@method_decorator(htmx_required, name="dispatch")
class DashboardComponentFormView(LoginRequiredMixin,HorillaSingleFormView):
    """
    Form view to dashboard component
    """

    template_name = "dashboard_component_form.html"
    model = DashboardComponent
    form_class = DashboardCreateForm
    condition_fields = ['field', 'operator', 'value']
    hidden_fields = ["company","config","is_active","dashboard","sequence","component_owner"]
    full_width_fields = ["name"]
    

    def get_initial(self):
        initial = super().get_initial()
        dashboard_id = self.request.GET.get('dashboard') or self.request.POST.get('dashboard')

        if dashboard_id:
            dashboard = Dashboard.objects.get(id=dashboard_id)
            initial['dashboard'] = dashboard
        company = getattr(_thread_local, "request", None).active_company if hasattr(_thread_local, "request") else self.request.user.company
        initial['company'] = company
        initial['component_owner'] = self.request.user

        initial.update(self.request.GET.dict())
        return initial
    

    def add_condition_row(self, request):
        row_id = request.GET.get('row_id', '0')
        
        new_row_id = '0'
        if row_id == 'next':
            current_count = request.session.get('condition_row_count', 0)
            current_count += 1
            request.session['condition_row_count'] = current_count
            new_row_id = str(current_count)
        else:
            try:
                new_row_id = str(int(row_id) + 1)
            except ValueError:
                new_row_id = '1'

        module = request.GET.get('module') or request.POST.get('module')
        if not module and hasattr(self, 'object') and self.object and self.object.module:
            module = self.object.module
        elif not module and 'initial' in self.get_form_kwargs() and 'module' in self.get_form_kwargs()['initial']:
            module = self.get_form_kwargs()['initial']['module']
        model_name = module  

        form_kwargs = self.get_form_kwargs()
        form_kwargs['row_id'] = new_row_id
        if module:
            form_kwargs['request'] = request
            form_kwargs['initial'] = form_kwargs.get('initial', {}) | {'module': module, 'model_name': model_name}
        else:
            form_kwargs['request'] = request
            form_kwargs['initial'] = form_kwargs.get('initial', {}) | {'module': '', 'model_name': ''}

        if 'pk' in self.kwargs:
            try:
                instance = self.model.objects.get(pk=self.kwargs['pk'])
                form_kwargs['instance'] = instance
            except self.model.DoesNotExist:
                pass
                    
        form = self.get_form_class()(**form_kwargs)
        
        context = {
            'form': form,
            'condition_fields': self.condition_fields or [],
            'row_id': new_row_id,
            'submitted_condition_data': self.get_submitted_condition_data(),
        }
        html = render_to_string('partials/condition_row.html', context, request=request)
        return HttpResponse(html)


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        model_name = self.request.GET.get('model_name') or self.request.POST.get('model_name') or self.request.GET.get('module')


        if model_name:
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            kwargs['initial']['model_name'] = model_name
            kwargs['initial']['module'] = model_name  # Sync module with model_name
        
        kwargs['condition_model'] = ComponentCriteria
        kwargs['request'] = self.request
        
        return kwargs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object and self.object.pk:
            existing_conditions = self.object.conditions.all().order_by('sequence')
            context['existing_conditions'] = existing_conditions
            form = context.get('form')
            if form and hasattr(form, 'condition_field_choices'):
                context['condition_field_choices'] = form.condition_field_choices
        
        form = context.get('form')
        if form and hasattr(form, 'instance') and form.instance.module:
            context['module'] = form.instance.module
        elif 'initial' in kwargs and 'module' in kwargs['initial']:
            context['module'] = kwargs['initial']['module']
        elif self.request.method == 'GET' and self.request.GET.get('module'):
            context['module'] = self.request.GET.get('module')
        else:
            context['module'] = ''  

        return context

    @cached_property
    def form_url(self):
        pk = self.kwargs.get('pk') or self.request.GET.get('id')
        base_url = reverse_lazy("dashboards:component_create") if not pk else reverse_lazy("dashboards:component_update", kwargs={"pk": pk})
        dashboard_id = self.request.GET.get('dashboard')
        if dashboard_id:
            return f"{base_url}?dashboard={dashboard_id}"
        return base_url
    

    def get(self, request, *args, **kwargs):
        component_id = self.kwargs.get("pk")
        if request.user.has_perm("dashboards.change_dashboard") or request.user.has_perm("dashboards.add_dashboard"):
            return super().get(request, *args, **kwargs)

        if component_id:
            component = get_object_or_404(DashboardComponent, pk=component_id)
            if component.component_owner == request.user:
                return super().get(request, *args, **kwargs)

        return render(request, "403.html")


    def form_valid(self, form):
        """Override to handle multiple condition rows"""
        if not self.request.user.is_authenticated:
            messages.error(self.request, "You must be logged in to perform this action.")
            return self.form_invalid(form)
        
        condition_rows = form.cleaned_data.get('condition_rows', [])
        
        try:
            with transaction.atomic():
                # Save the main ScoringCriterion
                self.object = form.save(commit=False)

                columns_data = form.cleaned_data.get('columns', '')

                if isinstance(columns_data, list):
                    self.object.columns = ','.join(columns_data)
                else:
                    self.object.columns = columns_data
                
                if self.kwargs.get('pk'):
                    self.object.updated_at = timezone.now()
                    self.object.updated_by = self.request.user
                else:
                    self.object.created_at = timezone.now()
                    self.object.created_by = self.request.user
                    self.object.updated_at = timezone.now()
                    self.object.updated_by = self.request.user
                
                self.object.company = getattr(_thread_local, "request", None).active_company if hasattr(_thread_local, "request") else self.request.user.company

                self.object.save()
                
                if self.kwargs.get('pk'):
                    self.object.conditions.all().delete()
                
                created_conditions = []
                for row_data in condition_rows:
                    condition = ComponentCriteria(
                        component=self.object,
                        field=row_data['field'],
                        operator=row_data['operator'],
                        value=row_data.get('value', ''),
                        sequence=row_data.get('sequence', 0),
                        created_at=timezone.now(),
                        created_by=self.request.user,
                        updated_at=timezone.now(),
                        updated_by=self.request.user,
                        company=getattr(_thread_local, "request", None).active_company if hasattr(_thread_local, "request") else self.request.user.company
                    )
                    condition.save()
                    created_conditions.append(condition)
                self.request.session['condition_row_count'] = 0
                self.request.session.modified = True 
            messages.success(self.request, _("Chart Added successfully!"))
                
        except Exception as e:
            messages.error(self.request, f"Error saving: {str(e)}")
            return self.form_invalid(form)
        
        return HttpResponse(headers={"HX-Refresh": "true"})
    

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
 

@method_decorator(permission_required_or_denied("dashboards.add_dashboard"), name="dispatch")
class ModuleFieldChoicesView(View):
    """
    Class-based view to return field choices for a selected module via HTMX.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to return a <select> element with field choices.
        """
        module = request.GET.get('module')
        row_id = request.GET.get('row_id', '0')
        
        field_name = f"field_{row_id}"
        field_id = f"id_field_{row_id}"

        if not module:
            return HttpResponse(f'<select name="{field_name}" id="{field_id}" class="js-example-basic-single headselect"><option value="">---------</option></select>')

        try:
            model = None
            for app_config in apps.get_app_configs():
                try:
                    model = apps.get_model(app_label=app_config.label, model_name=module.lower())
                    break
                except LookupError:
                    continue
            if not model:
                return HttpResponse(f'<select name="{field_name}" id="{field_id}" class="js-example-basic-single headselect"><option value="">---------</option></select>')
        except Exception:
            return HttpResponse(f'<select name="{field_name}" id="{field_id}" class="js-example-basic-single headselect"><option value="">---------</option></select>')

        model_fields = []
        for field in model._meta.get_fields():
            if field.concrete or field.is_relation:
                verbose_name = getattr(field, 'verbose_name', field.name)
                if field.is_relation:
                    verbose_name = f"{verbose_name}"
                model_fields.append((field.name, verbose_name))

        field_choices = [("", "Select Field")] + model_fields

        select_html = f'<select name="{field_name}" id="{field_id}" class="js-example-basic-single headselect"'
        
        select_html += f' hx-get="{reverse_lazy("horilla_generics:get_field_value_widget")}"'
        select_html += f' hx-target="#id_value_{row_id}_container"'
        select_html += ' hx-swap="innerHTML"'
        select_html += f' hx-include="[name=\\"{field_name}\\"],#id_value_{row_id},[name=\\"module\\"]"'
        select_html += f' hx-vals=\'{{"model_name": "{module}", "row_id": "{row_id}"}}\''
        select_html += ' hx-trigger="change,load"'
        select_html += '>'
        
        for value, label in field_choices:
            select_html += f'<option value="{value}">{label}</option>'
        select_html += '</select>'

        return HttpResponse(select_html)


@method_decorator(permission_required_or_denied("dashboards.add_dashboard"), name="dispatch")
class MetricFieldChoicesView(View):
    """
    View to return metric field choices for a selected module via HTMX.
    """
    def get(self, request, *args, **kwargs):
        module = request.GET.get('module')
        
        if not module:
            return HttpResponse('<select name="metric_field" id="id_metric_field" class="js-example-basic-single headselect"><option value="">---------</option></select>')

        try:
            model = None
            for app_config in apps.get_app_configs():
                try:
                    model = apps.get_model(app_label=app_config.label, model_name=module.lower())
                    break
                except LookupError:
                    continue
            
            if not model:
                return HttpResponse('<select name="metric_field" id="id_metric_field" class="js-example-basic-single headselect"><option value="">---------</option></select>')
        except Exception:
            return HttpResponse('<select name="metric_field" id="id_metric_field" class="js-example-basic-single headselect"><option value="">---------</option></select>')

        metric_fields = []
        for field in model._meta.get_fields():
            if field.concrete and not field.is_relation:
                field_name = field.name
                field_label = field.verbose_name or field.name
                
                if hasattr(field, 'get_internal_type'):
                    field_type = field.get_internal_type()
                    if field_type in ['IntegerField', 'FloatField', 'DecimalField', 'BigIntegerField', 
                                    'SmallIntegerField', 'PositiveIntegerField', 'PositiveSmallIntegerField',
                                    'CharField', 'TextField', 'BooleanField', 'DateField', 
                                    'DateTimeField', 'TimeField', 'EmailField', 'URLField']:
                        metric_fields.append((field_name, f"{field_label}"))
                    elif hasattr(field, 'choices') and field.choices:
                        metric_fields.append((field_name, f"{field_label}"))
            
            elif hasattr(field, 'related_model') and field.many_to_one:
                field_name = field.name
                field_label = field.verbose_name or field.name
                metric_fields.append((field_name, f"{field_label}"))

        field_choices = [("", "Select Metric Field")] + metric_fields

        select_html = '' \
        '<label for="id_metric_field" class="text-xs text-color-600">Metric Field</label>\
        <select name="metric_field" id="id_metric_field" class="js-example-basic-single headselect">'
        for value, label in field_choices:
            select_html += f'<option value="{value}">{label}</option>'
        select_html += '</select>'

        return HttpResponse(select_html)


@method_decorator(permission_required_or_denied("dashboards.add_dashboard"), name="dispatch")
class ColumnFieldChoicesView(View):
    """
    View to return metric field choices for a selected module via HTMX.
    """
    def get(self, request, *args, **kwargs):
        module = request.GET.get('module')
        
        if not module:
            return HttpResponse('<select name="columns" id="id_columns" class="js-example-basic-multiple headselect" multiple ><option value="">---------</option></select>')

        try:
            model = None
            for app_config in apps.get_app_configs():
                try:
                    model = apps.get_model(app_label=app_config.label, model_name=module.lower())
                    break
                except LookupError:
                    continue
            
            if not model:
                return HttpResponse('<select name="columns" id="id_columns" class="js-example-basic-multiple headselect" multiple><option value="">---------</option></select>')
        except Exception:
            return HttpResponse('<select name="columns" id="id_columns" class="js-example-basic-multiple headselect" multiple><option value="">---------</option></select>')

        column_fields = []
        for field in model._meta.get_fields():
            if field.concrete and not field.is_relation:
                field_name = field.name
                field_label = field.verbose_name or field.name
                
                if hasattr(field, 'get_internal_type'):
                        field_type = field.get_internal_type()
                        if field_type in ['CharField', 'TextField', 'BooleanField', 'DateField', 
                                        'DateTimeField', 'TimeField', 'EmailField', 'URLField']:
                            column_fields.append((field_name, field_label))
                        elif hasattr(field, 'choices') and field.choices:
                            column_fields.append((field_name, f"{field_label}"))
             # Include ForeignKey fields for grouping
            elif hasattr(field, 'related_model') and field.many_to_one:
                field_name = field.name
                field_label = field.verbose_name or field.name
                column_fields.append((field_name, f"{field_label}"))

        field_choices = [("", "Add Columns")] + column_fields

        select_html = '' \
        '<label for="id_columns" class=" pb-2 text-xs text-color-600">Table Columns</label>' \
        '<select name="columns" id="id_columns" class="js-example-basic-multiple headselect" multiple>'
        for value, label in field_choices:
            select_html += f'<option value="{value}">{label}</option>'
        select_html += '</select>'

        return HttpResponse(select_html)


@method_decorator(permission_required_or_denied("dashboards.add_dashboard"), name="dispatch")
class GroupingFieldChoicesView(View):
    """
    View to return grouping field choices for a selected module via HTMX.
    """
    def get(self, request, *args, **kwargs):
        module = request.GET.get('module')
        
        if not module:
            return HttpResponse('<select name="grouping_field" id="id_grouping_field" class="js-example-basic-single headselect"><option value="">---------</option></select>')

        try:
            model = None
            for app_config in apps.get_app_configs():
                try:
                    model = apps.get_model(app_label=app_config.label, model_name=module.lower())
                    break
                except LookupError:
                    continue
            
            if not model:
                return HttpResponse('<select name="grouping_field" id="id_grouping_field" class="js-example-basic-single headselect"><option value="">---------</option></select>')
        except Exception:
            return HttpResponse('<select name="grouping_field" id="id_grouping_field" class="js-example-basic-single headselect"><option value="">---------</option></select>')

        # Get fields suitable for grouping
        grouping_fields = []
        for field in model._meta.get_fields():
            if field.concrete and not field.is_relation:
                field_name = field.name
                field_label = field.verbose_name or field.name
                
                if hasattr(field, 'get_internal_type'):
                    field_type = field.get_internal_type()
                    if field_type in ['CharField', 'TextField', 'BooleanField', 'DateField', 
                                    'DateTimeField', 'TimeField', 'EmailField', 'URLField']:
                        grouping_fields.append((field_name, field_label))
                    elif hasattr(field, 'choices') and field.choices:
                        grouping_fields.append((field_name, f"{field_label}"))
            
            # Include ForeignKey fields for grouping
            elif hasattr(field, 'related_model') and field.many_to_one:
                field_name = field.name
                field_label = field.verbose_name or field.name
                grouping_fields.append((field_name, f"{field_label}"))

        field_choices = [("", "Select Grouping Field")] + grouping_fields

        select_html = '' \
        '<label for="id_grouping_field" class="text-xs text-color-600">Grouping Field</label>\
        <select name="grouping_field" id="id_grouping_field" class="js-example-basic-single headselect">'
        for value, label in field_choices:
            select_html += f'<option value="{value}">{label}</option>'
        select_html += '</select>'

        return HttpResponse(select_html)


@method_decorator(permission_required_or_denied("dashboards.add_dashboard"), name="dispatch")
class SecondaryGroupingFieldChoicesView(View):
    """
    View to return secondary grouping field choices for a selected module via HTMX.
    """
    def get(self, request, *args, **kwargs):
        module = request.GET.get('module')
        
        if not module:
            return HttpResponse('<select name="secondary_grouping" id="id_secondary_grouping" class="js-example-basic-single headselect"><option value="">---------</option></select>')

        try:
            model = None
            for app_config in apps.get_app_configs():
                try:
                    model = apps.get_model(app_label=app_config.label, model_name=module.lower())
                    break
                except LookupError:
                    continue
            
            if not model:
                return HttpResponse('<select name="secondary_grouping" id="id_secondary_grouping" class="js-example-basic-single headselect"><option value="">---------</option></select>')
        except Exception:
            return HttpResponse('<select name="secondary_grouping" id="id_secondary_grouping" class="js-example-basic-single headselect"><option value="">---------</option></select>')

        grouping_fields = []
        for field in model._meta.get_fields():
            if field.concrete and not field.is_relation:
                field_name = field.name
                field_label = field.verbose_name or field.name
                
                if hasattr(field, 'get_internal_type'):
                    field_type = field.get_internal_type()
                    if field_type in ['CharField', 'TextField', 'BooleanField', 'DateField', 
                                    'DateTimeField', 'TimeField', 'EmailField', 'URLField']:
                        grouping_fields.append((field_name, field_label))
                    elif hasattr(field, 'choices') and field.choices:
                        grouping_fields.append((field_name, f"{field_label}"))
            
            elif hasattr(field, 'related_model') and field.many_to_one:
                field_name = field.name
                field_label = field.verbose_name or field.name
                grouping_fields.append((field_name, f"{field_label}"))

        field_choices = [("", "Select Secondary Grouping Field")] + grouping_fields

        select_html = '' \
        '<label for="secondary_grouping" class="text-xs text-color-600">Secondary Grouping Field</label>\
        <select name="secondary_grouping" id="id_secondary_grouping" class="js-example-basic-single headselect">'
        for value, label in field_choices:
            select_html += f'<option value="{value}">{label}</option>'
        select_html += '</select>'

        return HttpResponse(select_html)


@method_decorator(permission_required_or_denied("dashboards.add_dashboard"), name="dispatch")
class ChartPreviewView(View):
    def get(self, request, *args, **kwargs):
        chart_type = request.GET.get('chart_type', '')
        component_type = request.GET.get('component_type', '')

        if component_type is None or component_type == 'None':
            component_type = ''
        if chart_type is None or chart_type == 'None':
            chart_type = ''

        if component_type == 'kpi':
            html = '''
            <div class="bg-white rounded-lg border border-primary-300 p-4 shadow-sm" style="width: 30vh;">
                <div class="flex flex-col space-y-2">
                    <h3 class="text-sm font-medium text-gray-500">Total Opportunities</h3>
                    <div class="flex items-baseline space-x-2">
                        <span class="text-2xl font-bold text-gray-900">$574.34</span>
                        <span class="text-sm font-medium text-green-600 bg-green-50 px-2 py-1 rounded">
                            +23%
                        </span>
                    </div>
                </div>
            </div>
            '''
            return HttpResponse(html)

        if component_type == 'table_data':
            html = '''
            <div class="overflow-x-auto">
                <table class="min-w-full bg-white border border-dark-50">
                    <thead>
                        <tr class="border border-dark-50">
                            <th class="py-2 px-4 border border-dark-50">Lead Title</th>
                            <th class="py-2 px-4 border border-dark-50">Lead Status</th>
                            <th class="py-2 px-4 border border-dark-50">Lead Owner</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="py-2 px-4 border border-dark-50">Lead 1</td>
                            <td class="py-2 px-4 border border-dark-50">Contacted</td>
                            <td class="py-2 px-4 border border-dark-50">Adam Luis</td>
                        </tr>
                        <tr>
                            <td class="py-2 px-4 border border-dark-50">Lead 2</td>
                            <td class="py-2 px-4 border border-dark-50">Open</td>
                            <td class="py-2 px-4 border border-dark-50">Ella Jackson</td>
                        </tr>
                        <tr>
                            <td class="py-2 px-4 border border-dark-50">Lead 3</td>
                            <td class="py-2 px-4 border border-dark-50">Contacted</td>
                            <td class="py-2 px-4 border border-dark-50">Amelia</td>
                        </tr>
                        <tr>
                            <td class="py-2 px-4 border border-dark-50">Lead 4</td>
                            <td class="py-2 px-4 border border-dark-50">Open</td>
                            <td class="py-2 px-4 border border-dark-50">Jacon</td>
                        </tr>
                        <tr>
                            <td class="py-2 px-4 border border-dark-50">Lead 5</td>
                            <td class="py-2 px-4 border border-dark-50">Not Contacted</td>
                            <td class="py-2 px-4 border border-dark-50">Ella Jackson</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            '''
            return HttpResponse(html)

        if component_type == 'chart' or (not component_type and chart_type):
            sample_data = {
                'column': {
                    'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'data': [120, 200, 150, 80, 70, 110, 130],
                    'labelField': 'Sample Data'
                },
                'bar': {
                    'labels': ['Category A', 'Category B', 'Category C', 'Category D'],
                    'data': [12, 19, 15, 17],
                    'labelField': 'Sample Data'
                },
                'pie': {
                    'labels': ['Sample A', 'Sample B', 'Sample C', 'Sample D'],
                    'data': [30, 25, 25, 20],
                    'labelField': 'Sample Data'
                },
                'donut': {
                    'labels': ['Sample 1', 'Sample 2', 'Sample 3'],
                    'data': [40, 35, 25],
                    'labelField': 'Sample Data'
                },
                'line': {
                    'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
                    'data': [10, 25, 15, 30, 28],
                    'labelField': 'Sample Data'
                },
                'stacked_vertical': {
                    'stackedData': {
                        'categories': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                        'series': [
                            {'name': 'Series 1', 'data': [10, 20, 15, 25, 30]},
                            {'name': 'Series 2', 'data': [5, 10, 8, 12, 15]}
                        ]
                    },
                    'labelField': 'Sample Data',
                    'hasMultipleGroups': True
                },
                'stacked_horizontal': {
                    'stackedData': {
                        'categories': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                        'series': [
                            {'name': 'Series 1', 'data': [10, 20, 15, 25, 30]},
                            {'name': 'Series 2', 'data': [5, 10, 8, 12, 15]}
                        ]
                    },
                    'labelField': 'Sample Data',
                    'hasMultipleGroups': True
                },
                'funnel': {
                    'labels': ['Leads', 'Qualified', 'Proposal', 'Negotiation', 'Closed'],
                    'data': [100, 75, 50, 30, 20],
                    'labelField': 'Sample Data'
                }
            }

            config = sample_data.get(chart_type)
            if config:
                chart_config = {
                    'type': chart_type,
                    **config
                }
                chart_config_json = json.dumps(chart_config)
                html = f'''
                <div id="preview-wrapper" class="w-full h-full relative overflow-hidden">
                    <div id="preview-chart-{chart_type}" class="w-full h-full" style="min-height: 200px;"></div>
                </div>
                <script>
                (function() {{
                    const chartDom = document.getElementById('preview-chart-{chart_type}');
                    if (chartDom && typeof EChartsConfig !== 'undefined' && typeof echarts !== 'undefined') {{
                        const myChart = echarts.init(chartDom);
                        const config = {chart_config_json};
                        const option = EChartsConfig.getChartOption(config);
                        myChart.setOption(option);
                    }}
                }})();
                </script>
                '''
                return HttpResponse(html)

        if not component_type and not chart_type:
            return HttpResponse('<div class="text-gray-500 text-sm flex items-center justify-center h-full">Select component type to see preview</div>')
        elif component_type and component_type != 'chart' and not chart_type:
            return HttpResponse(f'<div class="text-gray-500 text-sm flex items-center justify-center h-full">Preview for {component_type} component</div>')
        elif component_type == 'chart' and not chart_type:
            return HttpResponse('<div class="text-gray-500 text-sm flex items-center justify-center h-full">Select chart type to see preview</div>')
        else:
            return HttpResponse('<div class="text-gray-500 text-sm flex items-center justify-center h-full">Chart type not supported</div>')

  
@method_decorator(permission_required_or_denied(["dashboards.view_dashboard","dashboards.view_own_dashboard"]), name="dispatch")
class DashboardComponentChartView(View):
    """
    View to render chart data for dashboard components using ECharts.
    Handles chart components with ECharts and KPIs with custom HTML.
    """

    def get_kpi_data(self, component):
        """
        Calculate KPI data based on metric type and field from the component.
        Returns a dictionary with data and label for HTML rendering.
        """
        model = None
        for app_config in apps.get_app_configs():
            try:
                model = apps.get_model(app_label=app_config.label, model_name=component.module.lower())
                break
            except LookupError:
                continue

        if not model or not component.metric_field:
            return None

        try:
            queryset = get_queryset_for_module(self.request.user, model)
            conditions = component.conditions.all()

            for condition in conditions:
                if condition.operator == 'equals':
                    queryset = queryset.filter(**{condition.field: condition.value})
                elif condition.operator == 'not_equals':
                    queryset = queryset.exclude(**{condition.field: condition.value})
                elif condition.operator == 'contains':
                    queryset = queryset.filter(**{f'{condition.field}__icontains': condition.value})
                elif condition.operator == 'not_contains':
                    queryset = queryset.exclude(**{f'{condition.field}__icontains': condition.value})
                elif condition.operator == 'greater_than':
                    queryset = queryset.filter(**{f'{condition.field}__gt': condition.value})
                elif condition.operator == 'less_than':
                    queryset = queryset.filter(**{f'{condition.field}__lt': condition.value})

            if component.metric_type == 'count':
                value = queryset.count()
            elif component.metric_type == 'sum':
                value = queryset.aggregate(total=Sum(component.metric_field))['total'] or 0
            elif component.metric_type == 'average':
                value = queryset.aggregate(avg=Avg(component.metric_field))['avg'] or 0
            elif component.metric_type == 'minimum':
                value = queryset.aggregate(min=Min(component.metric_field))['min'] or 0
            elif component.metric_type == 'maximum':
                value = queryset.aggregate(max=Max(component.metric_field))['max'] or 0
            else:
                value = queryset.count()

            return {
                'value': float(value),
                'label': f"{component.metric_type.title()} of {component.metric_field.replace('_', ' ').title()}",
            }
        except Exception as e:
            return None


    def get_chart_data(self, component):
        """
        Retrieve chart data based on component configuration.
        Handles only chart-type components.
        """
        model = None
        for app_config in apps.get_app_configs():
            try:
                model = apps.get_model(app_label=app_config.label, model_name=component.module.lower())
                break
            except LookupError:
                continue

        if not model or component.component_type != 'chart':
            return None

        try:
            queryset = get_queryset_for_module(self.request.user, model)
            conditions = component.conditions.all()
            
            is_stacked_chart = component.chart_type in ['stacked_vertical', 'stacked_horizontal']
            
            x_axis_label = component.grouping_field.replace('_', ' ').title() if component.grouping_field else 'Category'

            if component.grouping_field:
                field = model._meta.get_field(component.grouping_field)
                
                if is_stacked_chart and component.secondary_grouping:
                    return self.get_stacked_chart_data(queryset, component, conditions, field, x_axis_label, model)
                
                for condition in conditions:
                    if condition.operator == 'equals':
                        queryset = queryset.filter(**{condition.field: condition.value})
                    elif condition.operator == 'not_equals':
                        queryset = queryset.exclude(**{condition.field: condition.value})
                    elif condition.operator == 'contains':
                        queryset = queryset.filter(**{f'{condition.field}__icontains': condition.value})
                    elif condition.operator == 'not_contains':
                        queryset = queryset.exclude(**{f'{condition.field}__icontains': condition.value})
                    elif condition.operator == 'greater_than':
                        queryset = queryset.filter(**{f'{condition.field}__gt': condition.value})
                    elif condition.operator == 'less_than':
                        queryset = queryset.filter(**{f'{condition.field}__lt': condition.value})
                
                if field.is_relation and hasattr(field.remote_field.model, 'name'):
                    queryset = queryset.values(f'{component.grouping_field}__name').annotate(value=Count('id'))
                else:
                    if component.metric_type == 'count':
                        queryset = queryset.values(component.grouping_field).annotate(value=Count('id'))
                    elif component.metric_type == 'sum':
                        queryset = queryset.values(component.grouping_field).annotate(value=Sum(component.metric_field))
                    elif component.metric_type == 'average':
                        queryset = queryset.values(component.grouping_field).annotate(value=Avg(component.metric_field))
                    elif component.metric_type == 'minimum':
                        queryset = queryset.values(component.grouping_field).annotate(value=Min(component.metric_field))
                    elif component.metric_type == 'maximum':
                        queryset = queryset.values(component.grouping_field).annotate(value=Max(component.metric_field))
                    else:
                        queryset = queryset.values(component.grouping_field).annotate(value=Count('id'))

                labels = []
                data = []
                
                for item in queryset:
                    label = item.get(f'{component.grouping_field}__name' if field.is_relation and hasattr(field.remote_field.model, 'name') else component.grouping_field)
                    if isinstance(label, (list, dict)):
                        label = str(label)
                    elif label is None:
                        label = 'None'
                    labels.append(label)
                    data.append(float(item['value']))

                return {
                    'labels': labels,
                    'data': data,
                    'labelField': component.grouping_field.replace('_', ' ').title(),
                    'x_axis_label': x_axis_label,
                    'is_condition_based': conditions.exists()
                }
            else:
                return None
        except Exception as e:
            return None


    def get_stacked_chart_data(self, queryset, component, conditions, field, x_axis_label, model):
        """Handle stacked chart data with grouping_field and secondary_grouping"""
        try:
            for condition in conditions:
                if condition.operator == 'equals':
                    queryset = queryset.filter(**{condition.field: condition.value})
                elif condition.operator == 'not_equals':
                    queryset = queryset.exclude(**{condition.field: condition.value})
                elif condition.operator == 'contains':
                    queryset = queryset.filter(**{f'{condition.field}__icontains': condition.value})
                elif condition.operator == 'not_contains':
                    queryset = queryset.exclude(**{f'{condition.field}__icontains': condition.value})
                elif condition.operator == 'greater_than':
                    queryset = queryset.filter(**{f'{condition.field}__gt': condition.value})
                elif condition.operator == 'less_than':
                    queryset = queryset.filter(**{f'{condition.field}__lt': condition.value})

            if field.is_relation and hasattr(field.remote_field.model, 'name'):
                categories = list(queryset.values_list(f'{component.grouping_field}__name', flat=True).distinct().order_by(f'{component.grouping_field}__name'))
            else:
                categories = list(queryset.values_list(component.grouping_field, flat=True).distinct().order_by(component.grouping_field))
            
            categories = [str(cat) if cat is not None else 'None' for cat in categories if cat is not None]
            
            secondary_field = model._meta.get_field(component.secondary_grouping) if component.secondary_grouping else None
            if not secondary_field:
                return None

            if secondary_field.is_relation and hasattr(secondary_field.remote_field.model, 'name'):
                secondary_values = list(queryset.values_list(f'{component.secondary_grouping}__name', flat=True).distinct())
            else:
                secondary_values = list(queryset.values_list(component.secondary_grouping, flat=True).distinct())
            
            secondary_values = [val for val in secondary_values if val is not None]

            series_data = []
            for secondary_value in secondary_values:
                display_value = secondary_value
                if secondary_field.is_relation and hasattr(secondary_field.remote_field.model, 'name'):
                    related_obj = secondary_field.remote_field.model.objects.filter(name=secondary_value).first()
                    if related_obj:
                        display_value = str(related_obj)
                elif isinstance(secondary_field, ForeignKey):
                    related_obj = secondary_field.remote_field.model.objects.filter(pk=secondary_value).first()
                    if related_obj:
                        display_value = str(related_obj)

                filtered_queryset = queryset.filter(**{component.secondary_grouping: secondary_value})
                
                # Aggregate data based on grouping_field
                if field.is_relation and hasattr(field.remote_field.model, 'name'):
                    grouped_data = filtered_queryset.values(f'{component.grouping_field}__name').annotate(value=Count('id'))
                    grouped_dict = {item[f'{component.grouping_field}__name']: item['value'] for item in grouped_data}
                else:
                    if component.metric_type == 'count':
                        grouped_data = filtered_queryset.values(component.grouping_field).annotate(value=Count('id'))
                    elif component.metric_type == 'sum':
                        grouped_data = filtered_queryset.values(component.grouping_field).annotate(value=Sum(component.metric_field))
                    elif component.metric_type == 'average':
                        grouped_data = filtered_queryset.values(component.grouping_field).annotate(value=Avg(component.metric_field))
                    elif component.metric_type == 'minimum':
                        grouped_data = filtered_queryset.values(component.grouping_field).annotate(value=Min(component.metric_field))
                    elif component.metric_type == 'maximum':
                        grouped_data = filtered_queryset.values(component.grouping_field).annotate(value=Max(component.metric_field))
                    else:
                        grouped_data = filtered_queryset.values(component.grouping_field).annotate(value=Count('id'))
                    
                    grouped_dict = {str(item[component.grouping_field]): item['value'] for item in grouped_data}
                
                series_values = []
                for category in categories:
                    series_values.append(float(grouped_dict.get(category, 0)))
                
                series_data.append({
                    'name': f"{component.secondary_grouping.replace('_', ' ').title()}: {display_value}",
                    'data': series_values
                })
            
            return {
                'labels': categories,
                'data': [],
                'stackedData': {
                    'categories': categories,
                    'series': series_data
                },
                'labelField': component.grouping_field.replace('_', ' ').title(),
                'x_axis_label': x_axis_label,
                'hasMultipleGroups': True,
                'is_condition_based': conditions.exists()
            }
            
        except Exception as e:
            return None



    def get(self, request, *args, **kwargs):
        """
        Handle GET request to render the chart or KPI component.
        Uses ECharts for charts and custom HTML for KPIs with modern card design.
        """
        component_id = kwargs.get('component_id')
        try:
            component = DashboardComponent.objects.get(id=component_id)
            if component.component_type == 'kpi':
                kpi_data = self.get_kpi_data(component)
                if not kpi_data:
                    return HttpResponse(
                        '<div class="text-gray-500 text-sm flex items-center justify-center h-full">No KPI data available</div>'
                    )
                
                bg_colors = [
                    'bg-[#FFF3E0]',  # Light orange
                    'bg-[#E8F5E8]',  # Light green
                    'bg-[#FFE1F4]',  # Light pink
                    'bg-[#E3F2FD]',  # Light blue
                    'bg-[#F3E5F5]',  # Light purple
                    'bg-[#E0F2F1]',  # Light teal
                ]
                
                icon_colors = [
                    'text-orange-500',  # Orange
                    'text-green-500',   # Green
                    'text-pink-500',    # Pink
                    'text-blue-500',    # Blue
                    'text-purple-500',  # Purple
                    'text-teal-500',    # Teal
                ]
                
                bg_color = bg_colors[component.id % len(bg_colors)]
                icon_color = icon_colors[component.id % len(icon_colors)]
                
                icon_html = f'''
                    <div class="{bg_color} p-3 rounded-xl">
                        <i class="fas fa-chart-line {icon_color}"></i>
                    </div>
                '''
                
                if component.icon:
                    icon_html = f'''
                        <div class="{bg_color} p-3 rounded-xl">
                            <img src="{component.icon.url}" alt="KPI Icon" class="w-6 h-6 object-contain">
                        </div>
                    '''
                
                formatted_value = kpi_data['value']
                if component.metric_type in ['sum', 'average'] and ('price' in component.metric_field.lower() or 'amount' in component.metric_field.lower() or 'cost' in component.metric_field.lower()):
                    formatted_value = f"${kpi_data['value']:,.2f}"
                elif component.metric_type == 'count':
                    formatted_value = f"{int(kpi_data['value']):,}"
                else:
                    formatted_value = f"{kpi_data['value']:,.2f}"
                
                
                html = f'''
                    <div class="bg-white p-6 rounded-xl shadow-sm w-full relative">
                        <!-- Dropdown positioned absolutely in top-right -->
                        <div class="absolute top-4 right-4">
                            <div class="relative dropdown-wrapper ">
                                <button 
                                    id="dropdownbtn-{component.id}" 
                                    type="button"
                                    class="flex items-center justify-center w-6 h-6 rounded-md hover:bg-gray-100 transition-colors z-0 relative"
                                >
                                    <i class="fa fa-ellipsis-h" aria-hidden="true"></i>
                                </button>
                                <div class="dropdown-content absolute bg-white rounded-lg shadow-lg min-w-[150px] py-2 right-0 border border-gray-200 z-[9]">
                                    <ul class="text-sm py-1" aria-labelledby="dropdownbtn-{component.id}">
                                        <li>
                                            <a href="#" class="px-4 py-1.5 hover:text-primary-600 hover:bg-gray-50 transition duration-300 text-sm gap-4 items-center flex w-full"
                                            hx-get="/dashboards/component-update/{component.id}/?{request.GET.urlencode()}" 
                                            onclick="openModal()"
                                            hx-target="#modalBox"
                                            hx-swap="innerHTML">
                                                Update
                                            </a>
                                        </li>
                                        <li>
                                            <a href="#" 
                                                class="px-4 py-1.5 hover:text-primary-600 hover:bg-gray-50 transition duration-300 text-sm gap-4 items-center flex w-full"
                                                hx-post="/dashboards/component-delete/{component.id}/"
                                                hx-target="#deleteModeBox"
                                                hx-swap="innerHTML" 
                                                hx-trigger="click"
                                                onclick="openDeleteModeModal();"
                                                hx-vals='{{"check_dependencies": "true"}}'
                                                >
                                                Delete
                                            </a>
                                        </li>
                                        <li>
                                            <a href="#" 
                                                class="px-4 py-1.5 hover:text-primary-600 hover:bg-gray-50 transition duration-300 text-sm gap-4 items-center flex w-full"
                                                hx-get="/dashboards/move-to-another-dashboard/{component.id}/"
                                                hx-target="#modalBox"
                                                hx-swap="innerHTML" 
                                                hx-trigger="click"
                                                onclick="openModal()">
                                                Add to Another Dashboard
                                            </a>
                                        </li>   
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <div class="flex items-center gap-4 pr-8">
                            {icon_html}
                            <div>
                                <p class="text-gray-500 text-sm mb-1">{component.name}</p>
                                <div class="flex items-center gap-3">
                                    <p class="text-2xl font-bold text-gray-900">
                                        {formatted_value}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                '''
                return HttpResponse(html)
            else:  # Chart components
                chart_data = self.get_chart_data(component)
                if not chart_data:
                    return HttpResponse(
                        '<div class="text-gray-500 text-sm flex items-center justify-center h-full">No data available</div>'
                    )

                conditions = component.conditions.all()
                if conditions.exists():
                    condition_text = "Conditions: " + ", ".join(
                        [f"{cond.field} {cond.get_operator_display()} {cond.value}" for cond in conditions]
                    )
                    chart_data['title'] = {
                        'subtext': condition_text,
                        'subtextStyle': {'fontSize': 12},
                        'bottom': 0
                    }

                chart_config = {
                    'type': component.chart_type,
                    **chart_data
                }
                chart_config_json = json.dumps(chart_config)
                html = f'''
                <div id="component-chart-{component.id}" class="w-full h-full" style="min-height: 200px;"></div>
                <script>
                (function() {{
                    const chartDom = document.getElementById('component-chart-{component.id}');
                    if (chartDom && typeof EChartsConfig !== 'undefined' && typeof echarts !== 'undefined') {{
                        const myChart = echarts.init(chartDom);
                        const config = {chart_config_json};
                        const option = EChartsConfig.getChartOption(config);
                        myChart.setOption(option);
                    }}
                }})();
                </script>
                '''
                return HttpResponse(html)

        except DashboardComponent.DoesNotExist:
            return HttpResponse(
                '<div class="text-gray-500 text-sm flex items-center justify-center h-full">Component not found</div>'
            )
        except Exception as e:
            return HttpResponse(
                f'<div class="text-gray-500 text-sm flex items-center justify-center h-full">Error: {str(e)}</div>'
            )
        

@method_decorator(permission_required_or_denied("dashboards.delete_dashboard"), name="dispatch")
class ComponentDeleteView(LoginRequiredMixin,HorillaSingleDeleteView):
    model = DashboardComponent
    def get_post_delete_response(self):
        return HttpResponse(headers={"HX-Refresh": "true"})
    

@method_decorator(htmx_required, name="dispatch")
class AddToDashboardForm(LoginRequiredMixin,HorillaSingleFormView):
    """
    View to handle adding a component to another dashboard.
    """
    model = DashboardComponent  
    modal_height = False
    form_title = _("Move to Dashboard")
    fields = ['dashboard']
    full_width_fields = ['dashboard']


    def get_form_kwargs(self):
        """
        Pass the request to the form for queryset filtering and validation.
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        id = self.kwargs.get('component_id') 
        if id:
            component = DashboardComponent.objects.get(pk=self.kwargs.get('component_id'))
            initial['dashboard'] = component.dashboard
        return initial
    
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = getattr(self.request, 'user', None)
        if user:
            form.fields['dashboard'].widget.attrs.update({
                'class': 'js-example-basic-single',
            })
            if not user.is_superuser:
                form.fields['dashboard'].queryset = Dashboard.objects.filter(dashboard_owner=user)
        return form
    

    @cached_property
    def form_url(self):
        pk = self.kwargs.get('component_id') or self.request.GET.get('id')
        if pk:
            return reverse_lazy("dashboards:move_to_another_dashboard", kwargs={"component_id": pk})
        

    def get(self, request, *args, **kwargs):
        component_id = self.kwargs.get("component_id")
        if request.user.has_perm("dashboards.change_dashboard") or request.user.has_perm("dashboards.add_dashboard"):
            return super().get(request, *args, **kwargs)

        if component_id:
            dashboard = get_object_or_404(Dashboard, pk=component_id)
            if dashboard.dashboard_owner == request.user:
                return super().get(request, *args, **kwargs)

        return render(request, "403.html")
        
    
    def form_valid(self, form):
        target_dashboard = form.cleaned_data['dashboard']
        component_id = self.kwargs.get('component_id')

        try:
            original = DashboardComponent.objects.get(pk=component_id)
        except DashboardComponent.DoesNotExist:
            messages.error(self.request, _("Original component not found."))
            return HttpResponse(status=404)

        with transaction.atomic():
            field_names = [f.name for f in DashboardComponent._meta.fields if f.name not in ['id', 'pk', 'dashboard']]
            new_component = DashboardComponent(dashboard=target_dashboard)
            for field in field_names:
                setattr(new_component, field, getattr(original, field))
            
            new_component.save()

            for crit in original.conditions.all():
                crit.pk = None
                crit.component = new_component
                crit.save()

        messages.success(self.request, _("Chart successfully added to another dashboard!"))
        return HttpResponse(headers={"HX-Refresh": "true"})


@method_decorator(htmx_required, name="dispatch")
class DashboardCreateForm(LoginRequiredMixin,HorillaSingleFormView):

    model = Dashboard
    modal_height = False
    fields = ['name','description','folder','is_default','dashboard_owner']
    full_width_fields = ['name','description','folder','dashboard_owner']
    hidden_fields = ["dashboard_owner"]


    @cached_property
    def form_url(self):
        pk = self.kwargs.get('pk') or self.request.GET.get('id')
        if pk:
            return reverse_lazy("dashboards:dashboard_update", kwargs={"pk": pk})
        return reverse_lazy("dashboards:dashboard_create")
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = getattr(self.request, 'user', None)
        if user:
            form.fields['folder'].widget.attrs.update({
                'class': 'js-example-basic-single',
            })
            if not user.is_superuser:
                form.fields['folder'].queryset = DashboardFolder.objects.filter(folder_owner=user)
        return form
    
    def get_initial(self):
        initial = super().get_initial()

        company = getattr(_thread_local, "request", None).active_company if hasattr(_thread_local, "request") else self.request.user.company
        initial['company'] = company
        initial['dashboard_owner'] = self.request.user

        initial.update(self.request.GET.dict())
        return initial
    

    def get(self, request, *args, **kwargs):
        dashboard_id = self.kwargs.get("pk") 
        if request.user.has_perm("dashboards.change_dashboard") or request.user.has_perm("dashboards.add_dashboard"):
            return super().get(request, *args, **kwargs)

        if dashboard_id:
            dashboard = get_object_or_404(Dashboard, pk=dashboard_id)
            if dashboard.dashboard_owner == request.user:
                return super().get(request, *args, **kwargs)

        return render(request, "403.html")


    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(headers={"HX-Refresh": "true"})
    
 
@method_decorator(permission_required_or_denied("dashboards.delete_dashboard"), name="dispatch")
class DashboardDeleteView(LoginRequiredMixin,HorillaSingleDeleteView):
    model = Dashboard
    def get_post_delete_response(self):
        return HttpResponse(headers={"HX-Refresh": "true"})
    

# folder areas
@method_decorator(htmx_required, name="dispatch")
class DashboardFolderCreate(LoginRequiredMixin, HorillaSingleFormView):
    model = DashboardFolder
    fields = ['name', 'folder_owner','description','parent_folder'] 
    modal_height = False
    full_width_fields = ['name', 'folder_owner','description','parent_folder']
    hidden_fields = ['parent_folder','folder_owner']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.kwargs.get('pk'):
            form.fields = {k: v for k, v in form.fields.items() if k in ['name']}
        return form

    def get_initial(self):
        initial = super().get_initial()
        pk = self.request.GET.get('pk')
        initial['parent_folder'] = pk if pk else None  
        initial['folder_owner'] = self.request.user
        return initial

    @cached_property
    def form_url(self):
        pk = self.kwargs.get('pk')
        if pk:
            return reverse_lazy("dashboards:dashboard_folder_update", kwargs={"pk": pk})
        return reverse_lazy("dashboards:dashboard_folder_create")

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(headers={"HX-Refresh": "true"}) 
    

    def get(self, request, *args, **kwargs):
        folder_id = self.kwargs.get("pk") 
        if request.user.has_perm("dashboards.change_dashboard") or request.user.has_perm("dashboards.add_dashboard"):
            return super().get(request, *args, **kwargs)

        if folder_id:
            folder = get_object_or_404(DashboardFolder, pk=folder_id)
            if folder.folder_owner == request.user:
                return super().get(request, *args, **kwargs)

        return render(request, "403.html")


class DashboardFolderFavoriteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            folder = DashboardFolder.objects.get(pk=kwargs['pk'])
            user = request.user

            if user.is_superuser or user.has_perm("dashboards.change_dashboardfolder") or folder.folder_owner == user:
                if user in folder.favourited_by.all():
                    folder.favourited_by.remove(user)
                    messages.success(request, f"Removed {folder.name} from favorites.")
                else:
                    folder.favourited_by.add(user)
                    messages.success(request, f"Added {folder.name} to favorites.")
                return HttpResponse(headers={"HX-Refresh": "true"})
            else:
                return render(request, "403.html")
            
        except Dashboard.DoesNotExist:
            return HttpResponse("<script>alert('Folder not found');</script>", status=404)
        except Exception as e:
            return HttpResponse(f"<script>alert('Error: {str(e)}');</script>", status=500)
    
    def get(self,request, *args, **kwargs):
        return render(request, "403.html")
        

@method_decorator(permission_required_or_denied(["dashboards.view_dashboardfolder","dashboards.view_own_dashboardfolder"]), name="dispatch")
class DashboardFolderListView(LoginRequiredMixin, HorillaListView):
    template_name = "dashboard_folder_detail.html"
    model = DashboardFolder
    view_id = "dashboard-folder-list-view"
    search_url = reverse_lazy("dashboards:dashboard_folder_list_view")
    main_url = reverse_lazy("dashboards:dashboard_folder_list_view")
    table_width = False
    bulk_select_option = False
    sorting_target = f"#tableview-{view_id}"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(parent_folder=None)
        return queryset

    @cached_property
    def columns(self):
        instance = self.model()
        return [
            (instance._meta.get_field("name").verbose_name, "name"),
            (instance._meta.get_field("description").verbose_name, "description"),
        ]
    
    @cached_property
    def action_method(self):
        action_method = ""
        if self.request.user.has_perm("dashboards.change_dashboardfolder") or self.request.user.has_perm("dashboards.delete_dashboardfolder") or self.request.user.has_perm("dashboards.view_own_dashboardfolder"):
            action_method = "actions"

        return action_method

    

    @cached_property
    def col_attrs(self):
        query_params = {}
        if "section" in self.request.GET:
            query_params["section"] = self.request.GET.get("section")
        query_string = urlencode(query_params)
        attrs = {}
        if self.request.user.has_perm("dashboards.view_dashboardfolder") or self.request.user.has_perm("dashboards.view_own_dashboardfolder"):
            attrs = {
                "hx-get": f"{{get_detail_view_url}}?{query_string}",
                "hx-target": "#mainContent",
                "hx-swap": "outerHTML",
                "hx-push-url": "true",
                "hx-select": "#mainContent",
                "style": "cursor:pointer",
                "class": "hover:text-primary-600",
            }
        return [
            {
                "name": {
                    **attrs,
                }
            }
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Folders"
        for folder in context['object_list']:
            folder.get_detail_view_url = reverse_lazy('dashboards:dashboard_folder_detail_list', kwargs={'pk': folder.pk})
        
        return context


@method_decorator(permission_required_or_denied(["dashboards.view_dashboard","dashboards.view_own_dashboard"]), name="dispatch")
class FolderDetailListView(LoginRequiredMixin, HorillaListView):
    template_name = "dashboard_folder_detail.html"
    model = DashboardFolder
    view_id = "dashboard-folder-detail-view"
    table_width = False
    bulk_select_option = False
    search_url = reverse_lazy("dashboards:dashboard_folder_detail_list")
    sorting_target = f"#tableview-{view_id}"

    @cached_property
    def columns(self):
        return [
            ("Name", "name"),
            ("Type", "get_item_type"),
        ]
    
    @cached_property
    def action_method(self):
        action_method = ""
        if self.request.user.has_perm("dashboards.change_dashboardfolder") or self.request.user.has_perm("dashboards.delete_dashboardfolder") or self.request.user.has_perm("dashboards.change_dashboard") or self.request.user.has_perm("dashboards.delete_dashboard"):
            action_method = "actions_detail"

        return action_method
    

    def get(self, request, *args, **kwargs):
        if not self.model.objects.filter(folder_owner_id=self.request.user,pk=self.kwargs["pk"]).first() and not self.request.user.has_perm("dashboards.view_dashboard"):
            return render(self.request,"403.html")
        return super().get(request, *args, **kwargs)
    

    def get_queryset(self):
        folder_id = self.kwargs.get('pk')
        return DashboardFolder.objects.filter(parent_folder__id=folder_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_id = self.kwargs.get('pk')
        
        folders = DashboardFolder.objects.filter(parent_folder__id=folder_id)
        dashboards = Dashboard.objects.filter(folder__id=folder_id)
        
        folders_list = list(folders)
        dashboards_list = list(dashboards)
        
        for folder in folders_list:
            folder.item_type = "Folder"
            folder.get_item_type = "Folder"
            folder.hx_target = "#mainContent"
            folder.hx_swap = "outerHTML"
            folder.hx_select = "#mainContent"
            folder.get_detail_view_url = reverse_lazy('dashboards:dashboard_folder_detail_list', kwargs={'pk': folder.pk})
            
        for dashboard in dashboards_list:
            dashboard.item_type = "Dashboard" 
            dashboard.get_item_type = "Dashboard"
            dashboard.hx_target = "#mainContent"
            dashboard.hx_swap = "outerHTML"
            dashboard.hx_select = "#mainContent"
            dashboard.get_detail_view_url = reverse_lazy('dashboards:dashboard_detail_view', kwargs={'pk': dashboard.pk})

        combined = folders_list + dashboards_list
        combined.sort(key=lambda x: x.name.lower())
        
        context['object_list'] = combined
        context['queryset'] = combined
        
        context['total_records_count'] = len(combined)
        
        title = DashboardFolder.objects.filter(id=folder_id).first()
        context['title'] = title.name if title else "All Folders"
        context['pk'] = folder_id

        query_params = QueryDict(mutable=True)
        if "section" in self.request.GET:
            query_params["section"] = self.request.GET.get("section")
        query_string = urlencode(query_params)

        context["col_attrs"] = {
            "name": {
                "hx-get": f"{{get_detail_view_url}}?{query_string}",
                "hx-target": "{hx_target}",
                "hx-swap": "{hx_swap}",
                "hx-push-url": "true",
                "hx-select": "{hx_select}",
                "style": "cursor:pointer",
                "class": "hover:text-primary-600",
            },
            "get_item_type": {}
        }

        breadcrumbs = []
        current_folder = DashboardFolder.objects.filter(id=folder_id).first()
        
        breadcrumbs.append({
            'name': 'All Folders',
            'url': f"{reverse_lazy('dashboards:dashboard_folder_list_view')}?{query_string}"
        })
        
        folder_chain = []
        temp_folder = current_folder
        while temp_folder:
            folder_chain.append(temp_folder)
            temp_folder = temp_folder.parent_folder
        
        folder_chain.reverse()
        
        for folder in folder_chain:
            breadcrumbs.append({
                'name': folder.name,
                'url': f"{reverse_lazy('dashboards:dashboard_folder_detail_list', kwargs={'pk': folder.id})}?{query_string}",
                'active': folder.id == int(folder_id)
            })
            
        context['breadcrumbs'] = breadcrumbs

        return context


@method_decorator(permission_required_or_denied("dashboards.delete_dashboardfolder"), name="dispatch")  
class FolderDeleteView(LoginRequiredMixin,HorillaSingleDeleteView):
    model = DashboardFolder
    def get_post_delete_response(self):
        return HttpResponse(headers={"HX-Refresh": "true"})


@method_decorator(htmx_required, name="dispatch")
class MoveDashboardView(LoginRequiredMixin,HorillaSingleFormView):
    model = Dashboard
    fields = ['folder']
    modal_height = False
    full_width_fields = ['folder']

    @cached_property
    def form_url(self):
        pk = self.kwargs.get('pk') or self.request.GET.get('id')
        if pk:
            return reverse_lazy("dashboards:move_dashboard_to_folder", kwargs={"pk": pk})
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request 
        return kwargs
    
    def get(self, request, *args, **kwargs):
        dashboard_id = self.kwargs.get("pk") 
        if request.user.has_perm("dashboards.change_dashboard") or request.user.has_perm("dashboards.add_dashboard"):
            return super().get(request, *args, **kwargs)

        if dashboard_id:
            dashboard = get_object_or_404(Dashboard, pk=dashboard_id)
            if dashboard.dashboard_owner == request.user:
                return super().get(request, *args, **kwargs)

        return render(request, "403.html")
    
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = getattr(self.request, 'user', None)
        if user:
            form.fields['folder'].widget.attrs.update({
                'class': 'js-example-basic-single',
            })
            if not user.is_superuser:
                form.fields['folder'].queryset = DashboardFolder.objects.filter(folder_owner=user)
        return form


@method_decorator(htmx_required, name="dispatch")
class MoveFolderView(LoginRequiredMixin,HorillaSingleFormView):
    model = DashboardFolder
    fields = ['parent_folder']
    modal_height = False
    full_width_fields = ['parent_folder']

    @cached_property
    def form_url(self):
        pk = self.kwargs.get('pk') or self.request.GET.get('id')
        if pk:
            return reverse_lazy("dashboards:move_folder_to_folder", kwargs={"pk": pk})
        
    def get(self, request, *args, **kwargs):
        folder_id = self.kwargs.get("pk") 
        if request.user.has_perm("dashboards.change_dashboard") or request.user.has_perm("dashboards.add_dashboard"):
            return super().get(request, *args, **kwargs)

        if folder_id:
            folder = get_object_or_404(DashboardFolder, pk=folder_id)
            if folder.folder_owner == request.user:
                return super().get(request, *args, **kwargs)

        return render(request, "403.html")
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = getattr(self.request, 'user', None)
        if user:
            form.fields['parent_folder'].widget.attrs.update({
                'class': 'js-example-basic-single',
            })
            if not user.is_superuser:
                form.fields['parent_folder'].queryset = DashboardFolder.objects.filter(folder_owner=user)
        return form


# favourite area 

@method_decorator(permission_required_or_denied(["dashboards.view_dashboard","dashboards.view_own_dashboard"]), name="dispatch")  
class FavouriteDashboardListView(LoginRequiredMixin,HorillaListView):

    model = Dashboard
    template_name = "favourite_dashboard.html"
    view_id = "favourite-dashboard-list"
    filterset_class = DashboardFilter
    search_url = reverse_lazy("dashboards:dashboard_favourite_list_view")
    main_url = reverse_lazy("dashboards:dashboard_favourite_list_view")
    table_width = False
    bulk_select_option = False
    sorting_target = f"#tableview-{view_id}"

    @cached_property
    def action_method(self):
        action_method = ""
        if self.request.user.has_perm("dashboards.change_dashboard") or self.request.user.has_perm("dashboards.delete_dashboard"):
            action_method = "actions"

        return action_method

    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Favourite Dashboards"
        return context
    

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(favourited_by=self.request.user)
        return queryset
  
    @cached_property
    def columns(self):
        instance = self.model()
        return [
            (instance._meta.get_field("name").verbose_name, "name"),
            (instance._meta.get_field("description").verbose_name, "description"),
            (instance._meta.get_field("folder").verbose_name, "folder"),
            
        ]
    

    @cached_property
    def col_attrs(self):
        query_params = {}
        if "section" in self.request.GET:
            query_params["section"] = self.request.GET.get("section")
        query_string = urlencode(query_params)
        attrs = {}
        if self.request.user.has_perm("dashboards.view_dashboard"):
            attrs = {
                "hx-get": f"{{get_detail_view_url}}?{query_string}",
                "hx-target": "#mainContent",
                "hx-swap": "outerHTML",
                "hx-push-url": "true",
                "hx-select": "#mainContent",
            }
        return [
            {
                "name": {
                    "style": "cursor:pointer",
                    "class": "hover:text-primary-600",
                    **attrs,
                }
            }
        ]


@method_decorator(permission_required_or_denied(["dashboards.view_dashboardfolder","dashboards.view_own_dashboardfolder"]), name="dispatch")  
class FavouriteFolderListView(HorillaListView):
    template_name = "favourite_folder.html"
    model = DashboardFolder
    table_width = False
    view_id = "favourite-folder-list-view"
    bulk_select_option = False
    sorting_target = f"#tableview-{view_id}"

    @cached_property
    def action_method(self):
        action_method = ""
        if self.request.user.has_perm("dashboards.change_dashboardfolder") or self.request.user.has_perm("dashboards.delete_dashboardfolder") or self.request.user.has_perm("dashboards.change_dashboard") or self.request.user.has_perm("dashboards.delete_dashboard"):
            action_method = "actions"

        return action_method


    @cached_property
    def columns(self):
        instance = self.model()
        return [
            (instance._meta.get_field("name").verbose_name, "name"),  
        ]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(parent_folder=None,favourited_by=self.request.user)
        return queryset  
    
    @cached_property
    def col_attrs(self):
        query_params = {}
        if "section" in self.request.GET:
            query_params["section"] = self.request.GET.get("section")
        query_string = urlencode(query_params)
        attrs = {}
        if self.request.user.has_perm("dashboards.view_dashboardfolder"):
            attrs = {
                "hx-get": f"{{get_detail_view_url}}?{query_string}",
                "hx-target": "#mainContent",
                "hx-swap": "outerHTML",
                "hx-select": "#mainContent",
                "hx-push-url": "true",
                "style": "cursor:pointer",
                "class": "hover:text-primary-600",
            
            }
        return [
            {
                "name": {
                    **attrs,
                }
            }
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Favourite Folders"
        return context


@method_decorator(permission_required_or_denied("dashboards.change_dashboard"), name="dispatch")  
class ReorderComponentsView(LoginRequiredMixin, View):
    """
    Handle the final save of component reordering (both regular components and KPIs)
    """
    def post(self, request, *args, **kwargs):
        dashboard_id = kwargs.get('dashboard_id')
        
        try:
            dashboard = get_object_or_404(Dashboard, id=dashboard_id)
            
            component_order = request.POST.getlist('component_order')
            reorder_type = request.POST.get('reorder_type', 'components')  
            
            if not component_order:
                return JsonResponse({
                    'success': False,
                    'error': 'No component order provided'
                }, status=400)
            
            if reorder_type == 'kpi':
                valid_components = DashboardComponent.objects.filter(
                    dashboard=dashboard,
                    id__in=component_order,
                    component_type='kpi'
                )
                component_type_filter = 'kpi'
                success_message = 'KPI components reordered successfully!'
            else:
                valid_components = DashboardComponent.objects.filter(
                    dashboard=dashboard,
                    id__in=component_order,
                    component_type__in=['chart', 'table_data']  # All non-KPI types
                )
                component_type_filter = 'non_kpi'
                success_message = 'Components reordered successfully!'
            
            valid_component_ids = list(valid_components.values_list('id', flat=True))
            
            valid_component_ids = [str(id) for id in valid_component_ids]
            
            invalid_ids = set(component_order) - set(valid_component_ids)
            if invalid_ids:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid component IDs: {", ".join(invalid_ids)}'
                }, status=400)
            
            with transaction.atomic():
                for index, component_id in enumerate(component_order):
                    DashboardComponent.objects.filter(
                        id=component_id,
                        dashboard=dashboard
                    ).update(sequence=index + 1)
            
            messages.success(request, _(success_message))
            
            return JsonResponse({
                'success': True,
                'message': success_message
            })
                        
        except Dashboard.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Dashboard not found'
            }, status=404)
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)
        

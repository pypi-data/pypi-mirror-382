
from django.apps import apps
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from horilla_core.models import HorillaCoreModel, HorillaUser, upload_path
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from horilla_utils.methods import render_template


class DashboardFolder(HorillaCoreModel):
    """Model for organizing dashboards in folders"""
    name = models.CharField(max_length=255, verbose_name="Folder Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    parent_folder = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='subfolders',
        verbose_name="Folder"
    )
    favourited_by = models.ManyToManyField(
        HorillaUser, 
        related_name='favourite_folders',
        blank=True,
        verbose_name="Favourited By"
    )
    folder_owner = models.ForeignKey(
        HorillaUser, 
        on_delete=models.PROTECT, 
        related_name='folders',
        verbose_name="Folder Owner"
    )

    OWNER_FIELDS = ['folder_owner']

    class Meta:
        ordering = ['name']
        verbose_name = "Dashboard Folder"
        verbose_name_plural = "Dashboard Folders"

    def __str__(self):
        return self.name  # Match ReportFolder's simple string representation

    def get_item_type(self):
        return "Folder"
    
    def get_detail_view_url(self):
        return reverse_lazy('dashboards:dashboard_folder_detail_list', kwargs={'pk': self.pk})
    
    def actions(self):
        return render_template(
            path="folder_custom_actions.html",
            context={"instance": self},
        )
    
    def actions_detail(self):
        return render_template(
            path="folder_actions_detail.html",
            context={"instance": self},
        )  


class Dashboard(HorillaCoreModel):
    """Main dashboard model"""
    dashboard_owner = models.ForeignKey(
        HorillaUser, 
        on_delete=models.PROTECT, 
        related_name='dashboards',
        verbose_name="Dashboard Owner"
    )
    name = models.CharField(max_length=255, verbose_name="Dashboard Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    folder = models.ForeignKey(
        DashboardFolder, 
        on_delete=models.CASCADE, 
        related_name='dashboards',
        blank=True,
        null=True,
        verbose_name="Folder"
    )
    is_default = models.BooleanField(default=False, verbose_name="Is Default")
    favourited_by = models.ManyToManyField(
        HorillaUser, 
        related_name='favourite_dashboards',
        blank=True,
        verbose_name="Favourited By"
    )

    OWNER_FIELDS = ["dashboard_owner"]

    class Meta:
        ordering = ['name']
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"

    def __str__(self):
        return self.name
    

    def get_item_type(self):
        return "Dashboard"
    
    def get_detail_view_url(self):
        return reverse_lazy('dashboards:dashboard_detail_view',kwargs={"pk": self.pk })
        
    
    def get_update_url(self):
        return reverse_lazy('dashboards:dashboard_update',kwargs={"pk": self.pk })
    
    def get_delete_url(self):
        return reverse_lazy('dashboards:dashboard_delete',kwargs={"pk": self.pk })
    
    def get_change_owner_url(self):
        return reverse_lazy('dashboards:dashboard_change_owner',kwargs={"pk": self.pk })
    
    def get_favourite_toggle_url(self):
        return reverse_lazy('dashboards:dashboard_toggle_favourite',kwargs={"pk": self.pk })
    
    def actions(self):
        """
        This method for get custom column for action.
        """

        return render_template(
        path="dashboard_custom_actions.html",
            context={"instance": self},
        )
    
    def actions_detail(self):
        """
        This method for get custom column for action.
        """

        return render_template(
        path="dashboard_actions_detail.html",
            context={"instance": self},
        )
    
    def save(self, *args, **kwargs):
        """Override save to ensure only one default dashboard per user/company"""
        if self.is_default:
            Dashboard.objects.filter(
                dashboard_owner=self.dashboard_owner,
                company=self.company,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)

    @classmethod
    def get_default_dashboard(cls, user):
        """Get the default dashboard for a user"""
        try:
            return cls.objects.filter(
                dashboard_owner=user,
                company=user.company,
                is_default=True,
                is_active=True
            ).first()
        except:
            return None


class DashboardComponent(HorillaCoreModel):
    """Individual components within a dashboard"""
    
    COMPONENT_TYPES = [
        ('chart', 'Charts'),
        ('table_data', 'Table Data'),
        ('kpi', 'KPI'),
    ]
    
    CHART_TYPES = [
        ('column', 'Column Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('funnel', 'Funnel'),
        ('bar', 'Bar Chart'),
        ('donut', 'Donut'),
        ('stacked_vertical','Stacked Vertical Chart'),
        ('stacked_horizontal','Stacked Horizontal Chart'),

    ]
    
    METRIC_TYPES = [
        ('count', 'Count'),
        ('sum', 'Sum'),
        ('average', 'Average'),
        ('min', 'Minimum'),
        ('max', 'Maximum'),
    ]

    MODULE_CHOICES = [
        ('lead', 'Lead'),
        ('opportunity', 'Opportunity'),
        ('campaign', 'Campaign'),
        ('contact', 'Contact'),
        ('account', 'Account'),
        ('activity', 'Activity'),
    ]
    
    OPERATORS = [
        ('equals', 'Equals'),
        ('not_equals', 'Not Equals'),
        ('greater_than', 'Greater Than'),
        ('less_than', 'Less Than'),
        ('greater_equal', 'Greater Than or Equal'),
        ('less_equal', 'Less Than or Equal'),
        ('contains', 'Contains'),
        ('not_contains', 'Does Not Contain'),
        ('starts_with', 'Starts With'),
        ('ends_with', 'Ends With'),
        ('is_null', 'Is Null'),
        ('is_not_null', 'Is Not Null'),
    ]

    dashboard = models.ForeignKey(
        Dashboard, 
        on_delete=models.CASCADE, 
        related_name='components',
        verbose_name="Dashboard"
    )
    name = models.CharField(max_length=255, verbose_name="Component Name")
    component_type = models.CharField(
        max_length=50, 
        choices=COMPONENT_TYPES, 
        verbose_name="Component Type"
    )
    chart_type = models.CharField(
        max_length=50, 
        choices=CHART_TYPES, 
        blank=True, 
        null=True,
        default="column",
        verbose_name="Chart Type"
    )
    
    # Module and metric configuration
    module = models.CharField(max_length=50, choices=MODULE_CHOICES,verbose_name="Module")
   
    metric_type = models.CharField(
        max_length=50, 
        choices=METRIC_TYPES, 
        default='count',
        blank=True, 
        null=True,
        verbose_name="Metric Type"
    )
    metric_field = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Metric Field"
    )
    
    # Grouping configuration
    grouping_field = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Grouping Field"
    )
    secondary_grouping = models.CharField(
        max_length =100,
        blank=True, 
        null=True,
        verbose_name="Secondary Grouping (For Stacked)"
    )

    columns = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Table Columns"
    )
    
    # Display and positioning
    sequence = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(1)],
        verbose_name="Sequence"
    )
    icon = models.ImageField(
        upload_to=upload_path,
        null=True,
        blank=True,
        verbose_name=_("KPI Icon"),
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    component_owner = models.ForeignKey(
        HorillaUser, 
        on_delete=models.PROTECT, 
        related_name='components',
        verbose_name="Component Owner"
    )

    OWNER_FIELDS = ['component_owner']

    class Meta:
        ordering = ['sequence', 'created_at']
        verbose_name = "Dashboard Component"
        verbose_name_plural = "Dashboard Components"

    def __str__(self):
        return f"{self.dashboard.name} - {self.name}"
    
    @property
    def model_class(self):
        """Get the actual model class"""
        if self.content_type:
            return self.content_type.model_class()
        return None


    def save(self, *args, **kwargs):
        """
        Override save to ensure KPI components get lower sequence numbers (appear first)
        """
        if not self.sequence:
            if self.component_type == 'kpi':
                max_kpi_sequence = DashboardComponent.objects.filter(
                    dashboard=self.dashboard,
                    component_type='kpi',
                    is_active=True
                ).aggregate(models.Max('sequence'))['sequence__max'] or 0
                self.sequence = max_kpi_sequence + 1
            else:
                max_sequence = DashboardComponent.objects.filter(
                    dashboard=self.dashboard,
                    is_active=True
                ).aggregate(models.Max('sequence'))['sequence__max'] or 0
                self.sequence = max_sequence + 1
        
        super().save(*args, **kwargs)




    @classmethod
    def reorder_components(cls, dashboard, component_order):
        """
        Reorder components, but keep KPI components at the top
        This method now only handles non-KPI components
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Get KPI components count to determine starting sequence for others
            kpi_count = cls.objects.filter(
                dashboard=dashboard,
                component_type='kpi',
                is_active=True
            ).count()
            
            # Update sequences for the reordered components
            for index, component_id in enumerate(component_order):
                try:
                    component = cls.objects.get(
                        id=component_id,
                        dashboard=dashboard,
                        is_active=True
                    )
                    # Only reorder non-KPI components
                    if component.component_type != 'kpi':
                        # Start after KPI components
                        component.sequence = kpi_count + index + 1
                        component.save(update_fields=['sequence'])
                except cls.DoesNotExist:
                    continue

    def get_columns_list(self):
        """Return columns as a list regardless of storage format"""
        if not self.columns:
            return []
        
        try:
            if isinstance(self.columns, str):
                if self.columns.startswith('['):
                    # JSON array format
                    import json
                    return json.loads(self.columns)
                else:
                    # Comma-separated format
                    return [col.strip() for col in self.columns.split(',') if col.strip()]
            elif isinstance(self.columns, list):
                return self.columns
            else:
                return []
        except:
            return []
        
    
    def get_columns_with_headers(self):
        """Return columns with their display headers"""
        columns_list = self.get_columns_list
        if not columns_list:
            return []
        
        try:
            model = None
            for app_config in apps.get_app_configs():
                try:
                    model = apps.get_model(app_label=app_config.label, model_name=self.module.lower())
                    break
                except LookupError:
                    continue
            
            if not model:
                return []
            
            columns_with_headers = []
            for column in columns_list:
                try:
                    field = model._meta.get_field(column)
                    verbose_name = field.verbose_name or column.replace('_', ' ').title()
                    columns_with_headers.append({
                        'field': column,
                        'header': verbose_name,
                        'is_foreign_key': hasattr(field, 'related_model') and field.many_to_one
                    })
                except:
                    # Field might not exist, use the column name as is
                    columns_with_headers.append({
                        'field': column,
                        'header': column.replace('_', ' ').title(),
                        'is_foreign_key': False
                    })
            
            return columns_with_headers
        except:
            return []


class ComponentCriteria(HorillaCoreModel):
    """Additional criteria/filters for components"""
    component = models.ForeignKey(
        DashboardComponent, 
        on_delete=models.CASCADE, 
        related_name='conditions',
        verbose_name="Component"
    )
    field = models.CharField(
        max_length=100,
        verbose_name="Field Name"
    )
    operator = models.CharField(
        max_length=50, 
        choices=DashboardComponent.OPERATORS,
        verbose_name="Operator"
    )
    value = models.CharField(max_length=255, blank=True, verbose_name="Value")
    sequence = models.PositiveIntegerField(
        default=1,
        verbose_name="Sequence"
    )

    class Meta:
        ordering = ['sequence']
        verbose_name = "Component Criteria"
        verbose_name_plural = "Component Criteria"

    def __str__(self):
        return f"{self.component.name} - {self.field} {self.operator} {self.value}"

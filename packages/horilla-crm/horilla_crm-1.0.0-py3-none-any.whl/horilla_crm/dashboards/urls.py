from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    # Define your URL patterns here
    path("", views.HomePageView.as_view(), name="home_view"),
    path('dashboard-view/',views.DashboardView.as_view(),name="dashboard_view"),
    path('dashboard-list-view/',views.DashboardListView.as_view(),name="dashboard_list_view"),
    path('dashboard-nav-view/',views.DashboardNavbar.as_view(),name="dashboard_nav_view"),
    path('dashboard-detail-view/<int:pk>/',views.DashboardDetailView.as_view(),name="dashboard_detail_view"),
    path('component-create/',views.DashboardComponentFormView.as_view(),name="component_create"),
    path('component-update/<int:pk>/',views.DashboardComponentFormView.as_view(),name="component_update"),
    path('preview-chart/', views.ChartPreviewView.as_view(), name='preview_chart'),
    path('get-module-field-choices/', views.ModuleFieldChoicesView.as_view(), name='get_module_field_choices'),
    path('get-metric-field-choices/', views.MetricFieldChoicesView.as_view(), name='get_metric_field_choices'),
    path('get-grouping-field-choices/', views.GroupingFieldChoicesView.as_view(), name='get_grouping_field_choices'),
    path('get-secondary-grouping-field-choices/', views.SecondaryGroupingFieldChoicesView.as_view(), name='get_secondary_grouping_field_choices'),
    path('component-chart/<int:component_id>/', views.DashboardComponentChartView.as_view(), name='component_chart'),
    path('get-columns-field-choices/', views.ColumnFieldChoicesView.as_view(), name='get_columns_field_choices'),
    path('component-table-data/<int:component_id>/', views.DashboardComponentTableDataView.as_view(), name='component_table_data'),
    path('component-delete/<int:pk>/', views.ComponentDeleteView.as_view(), name='component_delete'),
    path('move-to-another-dashboard/<int:component_id>/', views.AddToDashboardForm.as_view(), name='move_to_another_dashboard'),
    path('dashboard-create/', views.DashboardCreateForm.as_view(), name='dashboard_create'),
    path('dashboard-update/<int:pk>/', views.DashboardCreateForm.as_view(), name='dashboard_update'),
    path('dashboard-delete/<int:pk>/', views.DashboardDeleteView.as_view(), name='dashboard_delete'),
    path('dashboard-toggle-favourite/<int:pk>/', views.DashboardFavoriteToggleView.as_view(), name='dashboard_toggle_favourite'),

    #folder area
    path('dashboard-folder-create/', views.DashboardFolderCreate.as_view(), name='dashboard_folder_create'),
    path('dashboard-folder-update/<int:pk>/', views.DashboardFolderCreate.as_view(), name='dashboard_folder_update'),
    path('dashboard-folder-list-view/', views.DashboardFolderListView.as_view(), name='dashboard_folder_list_view'),
    path('dashboard-folder-view/', views.DashboardView.as_view(), name='dashboard_folder_view'),
    path('dashboard-folder-favourite/<int:pk>/', views.DashboardFolderFavoriteView.as_view(), name='dashboard_folder_favourite'),
    path('dashboard-folder-delete/<int:pk>/',views.FolderDeleteView.as_view(),name="dashboard_folder_delete"),
    path("dashboard-folder-detail-list/<int:pk>/",views.FolderDetailListView.as_view(),name="dashboard_folder_detail_list"),
    path('move-dashboard-to-folder/<int:pk>/', views.MoveDashboardView.as_view(), name='move_dashboard_to_folder'),
    path('move-folder-to-folder/<int:pk>/', views.MoveFolderView.as_view(), name='move_folder_to_folder'),

    # favourite area
    path('dashboard-favourite-list-view/', views.FavouriteDashboardListView.as_view(), name='dashboard_favourite_list_view'),
    path('dashboard-favourite-view/', views.DashboardView.as_view(), name='dashboard_favourite_view'),
    path('folder-favourite-list-view/',views.FavouriteFolderListView.as_view(),name="folder_favourite_list_view"),
    path('folder-favourite-view/', views.DashboardView.as_view(), name='folder_favourite_view'),


    path('dashboard-save-component-order/<int:dashboard_id>/',views.ReorderComponentsView.as_view(),name='reorder_components'),
    
    


    

]


    


from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
   path('accounts-view/',views.AccountView.as_view(),name="accounts_view"),
   path("accounts-nav-view/", views.AccountsNavbar.as_view(), name="accounts_nav_view"),
   path("accounts-list-view/", views.AccountListView.as_view(), name="accounts_list_view"),
   path("accounts-kanban-view/", views.AccountsKanbanView.as_view(), name="accounts_kanban_view"),
   path("account-create-form-view/", views.AccountFormView.as_view(), name="account_create_form_view"),
   path("account-delete-view/<int:pk>/", views.AccountDeleteView.as_view(), name="account_delete_view"),
   path("account-edit-form-view/<int:pk>/", views.AccountFormView.as_view(), name="account_edit_form_view"),
   path("account-change-owner/<int:pk>/", views.AccountChangeOwnerForm.as_view(), name="account_change_owner"),
   path("account-detail-view/<int:pk>/", views.AccountDetailView.as_view(), name="account_detail_view"),
   path("account-detail-view-tabs/", views.AccountDetailViewTabs.as_view(), name="account_detail_view_tabs"),
   path("account-details-tab-view/<int:pk>/", views.AccountDetailsTab.as_view(), name="account_details_tab_view"),
   path("account-activity-tab-view/<int:pk>/", views.AccountActivityTab.as_view(), name="account_activity_tab_view"),
   path("account-nots-attachments/<int:pk>/",views.AccountsNotesAndAttachments.as_view(),name="account_notes_attachements"),
   path("account-related-list-tab-view/<int:pk>/", views.AccountRelatedListsTab.as_view(), name="account_related_list_tab_view"),
   path("account-history-tab-view/<int:pk>/", views.AccountHistoryTab.as_view(), name="account_history_tab_view"),
   path('create-account-contact-relation/',views.AddRelatedContactFormView.as_view(),name="create_account_contact_relation"),
   path('update-account-contact-relation/<int:pk>/',views.AddRelatedContactFormView.as_view(),name="edit_account_contact_relation"),
   path('child-account-add/', views.AddChildAccountFormView.as_view(), name='create_child_accounts'),
   path('child-account-edit/<int:pk>/', views.AddChildAccountFormView.as_view(), name='edit_child_account'),
   path('account-partner-create-form/', views.AccountPartnerFormView.as_view(), name='account_partner_create_form'),
   path('account-partner-update-form/<int:pk>/', views.AccountPartnerFormView.as_view(), name='account_partner_update_form'),
   
   

]

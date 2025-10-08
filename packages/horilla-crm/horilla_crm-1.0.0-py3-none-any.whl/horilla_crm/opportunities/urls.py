from django.urls import path
from . import views
from . import opporunity_stages,opportunity_team
from . import big_deal_alert as big_deal_alert_views

app_name = 'opportunities'

urlpatterns = [
    
   path("opportunities-view/", views.OpportunityView.as_view(),name="opportunities_view"),
   path("opportunities-nav/",views.OpportunityNavbar.as_view(),name="opportunities_nav"),
   path("opportunities-list/",views.OpportunityListView.as_view(),name="opportunities_list"),
   path("opportunities-kanban/", views.OpportunityKanbanView.as_view(), name="opportunities_kanban"),
   path("opportunity-create/",views.OpportunityMultiStepFormView.as_view(),name="opportunity_create"),
   path("opportunity-edit/<int:pk>/",views.OpportunityMultiStepFormView.as_view(),name="opportunity_edit"),
   path("opportunity-delete/<int:pk>/", views.OpportunityDeleteView.as_view(), name="opportunity_delete"),
   path("opportunity-change-owner/<int:pk>/", views.OpportunityChangeOwnerForm.as_view(), name="opportunity_change_owner"), 
   path("opportunity-detail-view/<int:pk>/", views.OpportunityDetailView.as_view(), name="opportunity_detail_view"),
   path("opportunity-detail-view-tabs/", views.OpportunityDetailViewTabView.as_view(), name="opportunity_detail_view_tabs"), 
   path("opportunity-details-tab/<int:pk>/",views.OpportunityDetailTab.as_view(),name="opportunity_details_tab"),
   path("opportunity-activity-detail-view/<int:pk>/", views.OpportunityActivityTabView.as_view(), name="opportunity_activity_detail_view"),
   path("opportunity-notes-attachments/<int:pk>/", views.OpportunitiesNotesAndAttachments.as_view(), name="opportunity_notes_attachments"),
   path("opportunity-related-lists/<int:pk>/",views.OpportunityRelatedLists.as_view(),name="opportunity_related_lists"),
   path("opportunity-history-tab-view/<int:pk>/", views.OpportunityHistoryTabView.as_view(),name="opportunity_history_tab_view"),
   path("add-opportunity-contact-role/", views.OpportunityContactRoleFormview.as_view(), name="add_opportunity_contact_role"),
   path("edit-opportunity-contact-role/<int:pk>", views.OpportunityContactRoleFormview.as_view(), name="edit_opportunity_contact_role"),

   #opportunity stage urls

   path("opportunity-stage-view/", opporunity_stages.OpportunityStageView.as_view(), name="opportunity_stage_view"),
   path("opportunity-stage-nav-view/", opporunity_stages.OpportunityStageNavbar.as_view(), name="opportunity_stage_nav_view"),
   path("opportunity-stage-list-view/", opporunity_stages.OpportunityStageListView.as_view(), name="opportunity_stage_list_view"),
   path("change-opportunity-stage-final/<int:pk>/",opporunity_stages.ChangeFinalStage.as_view(),name="change_opportunity_stage_final"),
   path("edit-opportunity-stage/<int:pk>/",opporunity_stages.CreateOpportunityStage.as_view(),name="edit_opportunity_stage"),
   path("create-opportunity-stage/",opporunity_stages.CreateOpportunityStage.as_view(),name="create_opportunity_stage"),
   path('toggle-order-field/', opporunity_stages.OpportynityToggleOrderFieldView.as_view(), name='toggle_order_field'),
   path("delete-opportunity-stage/<int:pk>/",opporunity_stages.OpportunityStatusDeleteView.as_view(),name="delete_opportunity_stage"),
   path('update-opportunity-stage-order/', opporunity_stages.UpdateOpportunityStageOrderView.as_view(), name='update_opportunity_stage_order'),
    path(
        "company/<int:company_id>/load-opp-stages/",
        opporunity_stages.LoadOpportunityStagesView.as_view(),
        name="load_opp_stages",
    ),
    path(
        "company/<int:pk>/create-opp-stage-group/",
        opporunity_stages.CreateOppStageGroupView.as_view(),
        name="create_opp_stage_group",
    ),
    path(
        "company/<int:company_id>/custom-opp-stages-form/",
        opporunity_stages.CustomOppStagesFormView.as_view(),
        name="custom_opp_stage_form",
    ),
    path(
        "company/<int:company_id>/save-custom-opp-stages/",
        opporunity_stages.SaveCustomOppStagesView.as_view(),
        name="save_custom_opp_stages",
    ),


   #Big deal alert urls
   path("big-deal-alert-view/",big_deal_alert_views.BigDealAlertView.as_view(),name="big_deal_alert_view"),
   path("big-deal-alert-nav/",big_deal_alert_views.BigDealAlertNavbar.as_view(),name="big_deal_alert_nav"),
   path("big-deal-main-view/",big_deal_alert_views.BigDealAlertMainView.as_view(),name="big_deal_main_view"),
   path("update-status/<int:pk>/", big_deal_alert_views.UpdateAlertStatusView.as_view(), name="update_alert_status"),
   path("big-deal-create-form/", big_deal_alert_views.BigDealAlertFormView.as_view(), name="big_deal_create_form"),
   path("big-deal-update-form/<int:pk>/", big_deal_alert_views.BigDealAlertFormView.as_view(), name="big_deal_update_form"),
   path("big-deal-delete/<int:pk>/", big_deal_alert_views.BigDealAlertDelete.as_view(), name="big_deal_delete"),

   #opportunity team urls
   path("opportunity-team-view/", opportunity_team.OpportunityTeamView.as_view(), name="opportunity_team_view"),
   path("opportunity-team-nav-view/", opportunity_team.OpportunityTeamNavbar.as_view(), name="opportunity_team_nav_view"),
   path("opportunity-team-list-view/", opportunity_team.OpportunityTeamListView.as_view(), name="opportunity_team_list_view"),
   path("edit-opportunity-team/<int:pk>/",opportunity_team.OpportunityTeamFormView.as_view(),name="edit_opportunity_team"),
   path("create-opportunity-team/",opportunity_team.OpportunityTeamFormView.as_view(),name="create_opportunity_team"),
   path(
        "opportunity-team-detail-view/<int:pk>/",
        opportunity_team.OpportunityTeamDetailView.as_view(),
        name="opportunity_team_detail_view",
    ),
    path(
        "opportunity-team-detail-nav-view/",
        opportunity_team.OpportunityTeamDetailNavbar.as_view(),
        name="opportunity_team_detail_nav_view",
    ),
    path(
        "opportunity-team-detail-list-view/",
        opportunity_team.OpportunityTeamDetailListView.as_view(),
        name="opportunity_team_detail_list_view",
    ),
   path("create-opportunity-team-member/",opportunity_team.OpportunityTeamMemberCreateView.as_view(),name="create_opportunity_team_member"),
   path("edit-opportunity-team-member/<int:pk>/",opportunity_team.OpportunityTeamMemberUpdateView.as_view(),name="edit_opportunity_team_member"),
   path("delete-opportunity-team/<int:pk>/",opportunity_team.OpportunityTeamDeleteView.as_view(),name="delete_opportunity_team"),
   path("delete-opportunity-team-member/<int:pk>/",opportunity_team.OpportunityTeamMembersDeleteView.as_view(),name="delete_opportunity_team_member"),
    path(
        "initialiaze-opportunity-stages/",
        opporunity_stages.InitializeDatabaseOpportunityStages.as_view(),
        name="initialiaze_opportunity_stages",
    ),




]
